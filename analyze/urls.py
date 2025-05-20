from django.urls import path
from analyze import views

app_name = 'analyze'
urlpatterns = [
    path('', views.index, name='index'),
    path('gallery', views.gallery, name='gallery'),
    path('add_to_cart', views.add_to_cart, name='add_to_cart'),
    path('text', views.get_text, name='text'),
    path('upload/', views.FileUploadView.as_view(), name='upload'),
    path('upload/success', views.upload_success, name='upload_success'),
    path('cart', views.cart, name='cart'),
    path('cart_payment', views.cart_payment, name='cart_payment'),
    path('prices', views.prices, name='prices'),
]
