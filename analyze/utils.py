import json
import requests

from django_project import settings


class PhotoServiceAPI:
    def __init__(self):
        self._base_url = settings.PHOTO_SERVICE_URL
        self._auth_url = settings.PROXY_AUTH['TOKEN_URL']
        self._access_token = None
        self._refresh_token = None

    def make_request(self, request_method, create_url, second_try=False, *args, **kwargs):
        auth_headers = self._get_auth_headers()

        try:
            response = request_method(url=create_url(*args), timeout=10, headers=auth_headers, **kwargs)

            if response.status_code == 401:
                self._refresh_token()
                # В случае, если это первая попытка, обновляем токен и делаем ещё одну попытку.
                # Чтобы не возникло бесконечной рекурсии, используется "second_try" переменная
                if not second_try:
                    self.make_request(request_method, create_url, second_try=True, *args, **kwargs)

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

    # методы работы с токенами
    def _authenticate(self):
        try:
            response = requests.post(
                url=self._auth_url,
                data={
                    'username': settings.PROXY_AUTH['USERNAME'],
                    'password': settings.PROXY_AUTH['PASSWORD'],
                },
            )
            response.raise_for_status()
            self._access_token = response.json()['access']
            self._refresh_token = response.json()['refresh']
        except requests.exceptions.RequestException as e:
            return e
        return response

    def _get_auth_headers(self):
        if not self._access_token:
            self._authenticate()
        return {'Authorization': f'Bearer {self._access_token}'}

    def _refresh_token(self):
        try:
            response = requests.post(
                url=f'{self._auth_url}/refresh',
                data={'refresh': self._refresh_token},
            )
            response.raise_for_status()
            self._access_token = response.json()['access']
        except requests.exceptions.RequestException as e:
            return e
        return response

    # Методы для обращения к адресам ручек
    def get_all_documents(self):
        return self.make_request(requests.get, self._url_all_documents, False)

    def get_document(self, path):
        return self.make_request(requests.get, self._url_document, False, path)

    def get_document_url(self, path):
        return self._url_document(path)

    def upload_document(self, **kwargs):
        return self.make_request(requests.post, self._url_upload_document, False, **kwargs)

    def delete_document(self, doc_id):
        return self.make_request(requests.delete, self._url_delete_document, False, doc_id)

    def add_task_to_analyze(self, doc_id, **kwargs):
        return self.make_request(requests.post, self._url_analyze_document, False, doc_id, **kwargs)

    def get_document_text(self, doc_id):
        return self.make_request(requests.get, self._url_text_document, False, doc_id)

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
