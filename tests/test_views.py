import pytest
from django.urls import reverse
from unittest.mock import Mock


# from analyze.views import gallery


@pytest.mark.django_db
def test_gallery_auth_redirect(client):
    response = client.get(reverse('analyze:gallery'))
    assert response.status_code == 302
    assert '/accounts/login/' in response.url


def test_gallery_view_authenticated(client, user, doc, user_to_doc, mocker):
    # Mock FastAPI response
    mock_response = Mock()
    mock_response.json.return_value = [{
        'id': 1,
        'path': 'test.jpg',
        'date': '2023-01-01T00:00:00.000'
    }]

    mocker.patch(
        'analyze.utils.PhotoServiceAPI.get_all_documents',
        return_value=mock_response
    )

    client.force_login(user)
    response = client.get(reverse('analyze:gallery'))

    assert response.status_code == 200
    assert len(response.context['docs']) == 1
    assert response.context['docs'][0]['image_url'] is not None
