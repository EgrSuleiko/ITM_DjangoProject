import requests
import json
from datetime import datetime
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from analyze.models import Doc, Price, UserToDoc
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

    for doc in displayed_docs:
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


@login_required()
def upload_success(request):
    return render(request, 'analyze/upload_success.html')


@login_required()
def cart(request):
    return render(request, 'analyze/cart.html')
