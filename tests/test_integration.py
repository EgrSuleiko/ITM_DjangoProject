from unittest.mock import Mock

import pytest
from django.urls import reverse

from analyze.models import Cart, Doc


@pytest.mark.django_db
def test_full_flow(client, user, price, mocker):
    mock_file = mocker.MagicMock()
    mock_file.name = 'test.png'
    mock_file.content_type = 'image/png'
    mock_file.size = 1024

    mock_upload = mocker.patch('analyze.utils.PhotoServiceAPI.upload_document')
    mock_response = Mock()
    mock_response.content = b'123'
    mock_upload.return_value = mock_response

    mocker.patch(
        'analyze.utils.PhotoServiceAPI.decode_response',
        return_value=123  # Возвращаем число вместо словаря
    )

    mocker.patch(
        'analyze.utils.PhotoServiceAPI.add_task_to_analyze',
        return_value=Mock(status_code=200)
    )

    client.force_login(user)

    response = client.post(
        reverse('analyze:upload'),
        {'file': mock_file}
    )

    doc = Doc.objects.first()
    assert doc.server_id == 123
    assert response.status_code == 302

    response = client.post(
        reverse('analyze:add_to_cart'),
        {'server_doc_id': 123}
    )
    assert response.status_code == 302

    response = client.get(reverse('analyze:cart'))
    assert response.status_code == 200
    assert 'cart' in response.context

    response = client.post(
        reverse('analyze:cart_payment'),
        {'cart_id': 1}
    )
    assert response.status_code == 302

    cart = Cart.objects.get(id=1)
    assert cart.payment is True
