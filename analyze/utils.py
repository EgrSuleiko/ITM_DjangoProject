import json
import requests

from django_project import settings


class PhotoServiceAPI:
    def __init__(self):
        self._base_url = settings.PHOTO_SERVICE_URL

    @staticmethod
    def make_request(request_method, create_url, *args, **kwargs):
        try:
            response = request_method(url=create_url(*args), timeout=10, **kwargs)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            return e
        else:
            return response

    @staticmethod
    def decode_response(response, encoding='utf-8'):
        try:
            return json.loads(response.content.decode(encoding=encoding))
        except json.decoder.JSONDecodeError as e:
            print(e)
            return None

    # Методы для обращения к адресам ручек
    def get_all_documents(self):
        return self.make_request(requests.get, self._url_all_documents)

    def get_document(self, path):
        return self.make_request(requests.get, self._url_document, path)

    def get_document_url(self, path):
        return self._url_document(path)

    def upload_document(self, **kwargs):
        return self.make_request(requests.post, self._url_upload_document, **kwargs)

    def delete_document(self, doc_id):
        return self.make_request(requests.delete, self._url_delete_document, doc_id)

    def add_task_to_analyze(self, doc_id, **kwargs):
        return self.make_request(requests.post, self._url_analyze_document, doc_id, **kwargs)

    def get_document_text(self, doc_id):
        return self.make_request(requests.get, self._url_text_document, doc_id)

    # Адреса для всех ручек
    def _url_all_documents(self):
        return self._base_url + '/documents'

    def _url_document(self, path):
        return self._base_url + '/documents/file/' + path

    def _url_upload_document(self):
        return self._base_url + '/documents/upload'

    def _url_delete_document(self, doc_id):
        return self._base_url + '/documents/delete/' + str(doc_id)

    def _url_analyze_document(self, doc_id):
        return self._base_url + '/documents/analyze/' + str(doc_id)

    def _url_text_document(self, doc_id):
        return self._base_url + '/documents/get_text/' + str(doc_id)
