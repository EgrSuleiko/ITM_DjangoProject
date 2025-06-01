from datetime import datetime
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from analyze.models import Doc, Price, UserToDoc, Cart
from analyze.forms import FileUploadForm
from analyze.utils import PhotoServiceAPI

photo_service = PhotoServiceAPI()


def index(request):
    return render(request, 'analyze/index.html')


@login_required
def gallery(request):
    all_docs = photo_service.get_all_documents()
    if isinstance(all_docs, Exception):
        return render(request, 'analyze/gallery.html', {'error': f'Ошибка загрузки файла {str(all_docs)}'})

    all_docs = all_docs.json()
    displayed_docs = []

    if all_docs:
        current_user_docs_server_ids = set(
            UserToDoc.objects.select_related('doc')
            .filter(user_id=request.user.id)
            .values_list('doc__server_id', flat=True)
        )
        paid_docs_server_ids = set(
            Doc.objects.filter(cart__payment=True)
            .values_list('server_id', flat=True)
            .distinct()
        )
        in_cart_docs_server_ids = set(
            Doc.objects.filter(cart__payment=False)
            .values_list('server_id', flat=True)
            .distinct()
        )

        for doc in all_docs:
            if doc['id'] in current_user_docs_server_ids:
                doc['paid'] = doc['id'] in paid_docs_server_ids
                doc['in_cart'] = doc['id'] in in_cart_docs_server_ids
                doc['image_url'] = photo_service.get_document_url(doc['path'])
                doc['image_file'] = photo_service.get_document(doc['path'])
                doc['date'] = datetime.strptime(doc['date'], '%Y-%m-%dT%H:%M:%S.%f')
                displayed_docs.append(doc)

        displayed_docs.sort(key=lambda d: d['date'], reverse=True)

    return render(request, 'analyze/gallery.html', {'docs': displayed_docs})


@login_required
def delete_document(request):
    server_doc_id = request.POST.get('server_doc_id')
    Doc.objects.get(server_id=server_doc_id).delete()
    photo_service.delete_document(server_doc_id)

    return redirect('analyze:gallery')


@login_required
def get_text(request):
    template_name = 'analyze/text.html'
    doc_id = request.POST.get('doc_id')

    context = {'doc_id': doc_id}

    response = photo_service.get_document_text(doc_id)
    if isinstance(response, Exception):
        context['error'] = str(response)
        return render(request, template_name, context)

    context['text'] = photo_service.decode_response(response).replace('\\n', '\n')

    return render(request, template_name, context)


def prices(request):
    price_list = Price.objects.all().order_by('price')
    return render(request, 'analyze/prices.html', {'prices': price_list})


class FileUploadView(LoginRequiredMixin, View):
    template_name = 'analyze/upload.html'

    def get(self, request):
        form = FileUploadForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = FileUploadForm(request.POST, request.FILES)

        file = request.FILES['file']
        response = photo_service.upload_document(files={'uploaded_file': (file.name, file, file.content_type)})
        if isinstance(response, Exception):
            return render(request, 'analyze/upload.html', {'form': form,
                                                           'error': f'Ошибка загрузки файла {str(response)}'})

        server_id = photo_service.decode_response(response)

        new_doc = Doc(server_id=server_id, file_type=file.content_type.split('/')[-1], size=file.size)
        new_doc.save()

        new_user_to_doc = UserToDoc(doc=new_doc, user_id=request.user.id)
        new_user_to_doc.save()
        return redirect('analyze:upload_success')


@login_required
def upload_success(request):
    return render(request, 'analyze/upload_success.html')


@login_required
def cart(request):
    if request.method == 'POST':
        selected_cart_ids = request.POST.getlist('selected_cart_ids')
        for cart_id in selected_cart_ids:
            proceed_payment_and_analyze(cart_id)

    cart_items = Cart.objects.filter(user_id=request.user.id)

    return render(request, 'analyze/cart.html', {'cart': cart_items})


@login_required
def cart_payment(request):
    cart_id = request.POST.get('cart_id')
    proceed_payment_and_analyze(cart_id)

    return redirect('analyze:cart')


@login_required
def add_to_cart(request):
    server_doc_id = request.POST.get('server_doc_id')

    doc = Doc.objects.get(server_id=server_doc_id)
    price_for_doc_type = Price.objects.get(file_type=doc.file_type)
    new_cart = Cart(order_price=price_for_doc_type.price * doc.size / 1024, user_id=request.user.id, doc_id=doc.id)
    new_cart.save()

    return redirect('analyze:gallery')


@login_required
def delete_from_cart(request):
    cart_id = request.POST.get('cart_id')
    Cart.objects.get(id=cart_id).delete()
    return redirect('analyze:cart')


def proceed_payment_and_analyze(cart_id):
    cart_item = Cart.objects.get(id=cart_id)
    language = cart_item.doc.language
    server_doc_id = cart_item.doc.server_id
    response = photo_service.add_task_to_analyze(server_doc_id, params={'language': language})
    if isinstance(response, Exception):
        return None

    cart_item.payment = True
    cart_item.save()
    return True


@login_required
def change_language(request):
    cart_id = request.POST.get('cart_id')
    cart_item = Cart.objects.get(id=cart_id)
    doc_item = cart_item.doc

    doc_item.language = 'rus' if doc_item.language == 'eng' else 'eng'
    doc_item.save()

    return redirect('analyze:cart')
