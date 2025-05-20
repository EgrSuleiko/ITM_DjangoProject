import requests
import json
from datetime import datetime
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from analyze.models import Doc, Price, UserToDoc, Cart
from analyze.forms import FileUploadForm

from django_project import settings


def index(request):
    return render(request, 'analyze/index.html')


@login_required()
def gallery(request):
    displayed_docs = []
    docs = []
    try:
        response = requests.get(f'{settings.PHOTO_SERVICE_URL}/documents')
        response.raise_for_status()
        docs = response.json()
    except requests.exceptions.RequestException as e:
        print(e)

    user_docs_server_id = set(
        UserToDoc.objects.select_related('doc')
        .filter(user_id=request.user.id)
        .values_list('doc__server_id', flat=True)
    )

    for doc in docs:
        if doc['id'] in user_docs_server_id:
            displayed_docs.append(doc)

    paid_docs_server_id = set(
        Doc.objects.filter(cart__payment=True)
        .values_list('server_id', flat=True)
        .distinct()
    )

    in_cart_docs_server_id = set(
        Doc.objects.filter(cart__payment=False)
        .values_list('server_id', flat=True)
        .distinct()
    )

    for doc in displayed_docs:
        doc['paid'] = doc['id'] in paid_docs_server_id
        doc['in_cart'] = doc['id'] in in_cart_docs_server_id
        doc['image_url'] = f'{settings.PHOTO_SERVICE_URL}/documents/file/{doc['path']}'
        doc['date'] = datetime.strptime(doc['date'], '%Y-%m-%dT%H:%M:%S.%f')

    context = {'docs': displayed_docs, 'settings': settings}
    return render(request, 'analyze/gallery.html', context)


def prices(request):
    prices = []

    prices = Price.objects.all().order_by('price')
    context = {'prices': prices}
    return render(request, 'analyze/prices.html', context)


class FileUploadView(LoginRequiredMixin, View):
    template_name = 'analyze/upload.html'

    def get(self, request):
        form = FileUploadForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = FileUploadForm(request.POST, request.FILES)

        file = request.FILES['file']
        try:
            response = requests.post(
                url=f'{settings.PHOTO_SERVICE_URL}/documents/upload',
                files={'uploaded_file': (file.name, file, file.content_type)},
                timeout=30
            )
            response.raise_for_status()

        except requests.exceptions.RequestException as e:
            return render(request, self.template_name, {'form': form,
                                                        'error': f'Ошибка загрузки файла {str(e)}'})

        try:
            response_content = json.loads(response.content.decode('utf-8'))
        except json.decoder.JSONDecodeError as e:
            return render(request, self.template_name, {'form': form,
                                                        'error': f'Ошибка загрузки файла {str(e)}'})

        new_doc = Doc(server_id=response_content, file_type=file.content_type.split('/')[-1], size=file.size)
        new_doc.save()

        new_user_to_doc = UserToDoc(doc=new_doc, user_id=request.user.id)
        new_user_to_doc.save()
        return redirect('analyze:upload_success')


def add_to_cart(request):
    server_doc_id = request.POST.get('server_doc_id')

    doc = Doc.objects.get(server_id=server_doc_id)
    price_for_doc_type = Price.objects.get(file_type=doc.file_type)
    new_cart = Cart(order_price=price_for_doc_type.price * doc.size / 1024, user_id=request.user.id, doc_id=doc.id)
    new_cart.save()

    return redirect('analyze:gallery')


def cart_payment(request):
    template_name = 'analyze/cart.html'
    cart_id = request.POST.get('cart_id')

    cart = Cart.objects.filter(id=cart_id)
    cart.update(payment=True)

    is_lang_rus = request.POST.get('rus_lang')

    server_doc_id = cart.select_related('doc').values_list('doc__server_id', flat=True)[0]
    try:
        response = requests.post(
            url=f'{settings.PHOTO_SERVICE_URL}/documents/analyze/{server_doc_id}',
            params={'language': 'rus' if is_lang_rus else 'eng'},
            timeout=30
        )
        response.raise_for_status()

    except requests.exceptions.RequestException as e:
        return render(request, template_name, {'error': f'Ошибка отправки файла на анализ {str(e)}'})

    return redirect('analyze:cart')


def cart(request):
    cart_items = Cart.objects.filter(user_id=request.user.id)
    context = {'cart': cart_items}

    return render(request, 'analyze/cart.html', context)


def get_text(request):
    template_name = 'analyze/text.html'
    doc_id = request.POST.get('doc_id')

    context = {'doc_id': doc_id}

    try:
        response = requests.get(
            url=f'{settings.PHOTO_SERVICE_URL}/documents/get_text/{doc_id}',
            timeout=30
        )
        response.raise_for_status()

        context['text'] = response.content.decode('utf-8')

    except requests.exceptions.RequestException as e:
        return render(request, template_name, {'error': f'Ошибка загрузки текста {str(e)}'})

    return render(request, template_name, context)


@login_required()
def upload_success(request):
    return render(request, 'analyze/upload_success.html')
