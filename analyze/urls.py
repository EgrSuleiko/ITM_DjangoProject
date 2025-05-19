from django.urls import path
from analyze import views

app_name = 'analyze'
urlpatterns = [
    path('', views.index, name='index'),
    path('gallery', views.gallery, name='gallery'),
    path('upload/', views.FileUploadView.as_view(), name='upload'),
    path('upload/success', views.upload_success, name='upload_success'),
    path('cart', views.cart, name='cart'),
    path('prices', views.prices, name='prices'),
]
