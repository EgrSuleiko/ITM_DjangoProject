import requests
from django.shortcuts import render
from analyze.models import Doc

from django_project import settings


def index(request):
    docs = []
    try:
        response = requests.get(f'{settings.PHOTO_SERVICE_URL}/documents')
        response.raise_for_status()
        docs = response.json()
    except requests.exceptions.RequestException as e:
        print(e)

    for doc in docs:
        doc['image_url'] = f'{settings.PHOTO_SERVICE_URL}/documents/file/{doc['path']}'

    context = {'docs': docs, 'settings': settings}
    return render(request, 'analyze/index.html', context)


def show_doc(request, doc_id):
    doc = Doc.objects.get(id=doc_id)
    context = {'doc': doc, 'settings': settings}
    return render(request, 'analyze/doc.html', context)



def upload_to_api(request):
    try:
        response = requests.post(f'{settings.PHOTO_SERVICE_URL}/documents/upload', files={'file': uploaded_file})
    except requests.exceptions.RequestException as e:
        print(e)
    return render(request, 'analyze/upload.html')


def add_doc(request):
    return render(request, 'analyze/upload.html')