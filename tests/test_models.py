def test_user_model(user):
    assert user.is_authenticated
    assert user.username == 'testuser'


def test_doc_model(doc):
    assert doc.file_type == 'png'
    assert doc.size == 256000
    assert doc.language == 'rus'


def test_price_model(price):
    assert price.price == 0.01
    assert str(price) == f'{price.id}: {price.file_type} - {price.price}/Kb'


def test_user_to_doc_model(user_to_doc, user, doc):
    assert user_to_doc.user == user
    assert user_to_doc.doc == doc


def test_cart_model(cart, doc, price):
    assert cart.order_price == doc.size * price.price / 1024
    assert not cart.payment
