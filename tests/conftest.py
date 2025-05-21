import pytest
from django.contrib.auth.models import User
from django.templatetags.i18n import language

from analyze.models import Doc, Price, UserToDoc, Cart


@pytest.fixture
def user(db):
    return User.objects.create_user(username='testuser', password='12345')


@pytest.fixture
def doc(db):
    return Doc.objects.create(server_id=1, file_type='png', size=256000, language='rus')


@pytest.fixture
def price(db):
    return Price.objects.create(file_type='png', price=0.01)


@pytest.fixture
def user_to_doc(db, user, doc):
    return UserToDoc.objects.create(user=user, doc=doc)


@pytest.fixture
def cart(db, user, doc, price):
    return Cart.objects.create(user=user, doc=doc, order_price=2.5)
