from unittest.mock import patch, Mock
from analyze.utils import PhotoServiceAPI
import requests


def test_photo_service_get_all_documents(mocker):
    mock_get = mocker.patch('requests.get')
    mock_response = Mock()
    mock_response.json.return_value = [{'id': 1}]
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    api = PhotoServiceAPI()
    response = api.get_all_documents()

    assert response.json() == [{'id': 1}]
    mock_get.assert_called_once_with(
        url=api._url_all_documents(),
        timeout=10
    )


def test_photo_service_upload_error(mocker):
    mocker.patch(
        'requests.post',
        side_effect=requests.exceptions.Timeout('Server timeout')
    )

    api = PhotoServiceAPI()
    result = api.upload_document(files={})

    assert isinstance(result, requests.exceptions.Timeout)
    assert 'Server timeout' in str(result)
