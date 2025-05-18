import requests
from django.shortcuts import render, redirect
from django.views import View

from analyze.models import Doc
from analyze.forms import FileUploadForm

from django_project import settings


class FileUploadView(View):
    template_name = 'analyze/upload.html'

    def get(self, request):
        form = FileUploadForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = FileUploadForm(request.POST, request.FILES)

        if not form.is_valid():
            return render(request, self.template_name, {'form': form, 'error': 'Некорректная форма'})

        try:
            file = request.FILES['file']
            response = requests.post(
                url=f'{settings.PHOTO_SERVICE_URL}/documents/upload',
                files={'uploaded_file': (file.name, file, file.content_type)},
                timeout=30
            )
            response.raise_for_status()

            return redirect('analyze:upload_success')

        except requests.exceptions.RequestException as e:
            return render(request, self.template_name, {'form': form,
                                                        'error': f'Ошибка загрузки файла {str(e)}',
                                                        'response': response})

        # except Exception as e:
        #     return render(request, self.template_name,
        #                   {'form': form, 'error': f'Ошибка {str(e)}'})


def upload_success(request):
    return render(request, 'analyze/upload_success.html')


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
