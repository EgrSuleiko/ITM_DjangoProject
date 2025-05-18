from django.urls import path
from analyze import views

app_name = 'analyze'
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:doc_id>/', views.show_doc, name='show_doc'),
    path('upload/', views.FileUploadView.as_view(), name='upload'),
    path('upload/success', views.upload_success, name='upload_success'),
]
