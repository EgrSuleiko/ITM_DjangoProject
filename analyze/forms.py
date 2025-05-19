from django import forms


class FileUploadForm(forms.Form):
    file = forms.FileField(
        label='Выберите файл',
        widget=forms.ClearableFileInput(attrs={'class': 'form-control-file', 'accept': 'image/*'}),
        help_text='Поддерживаются изображения формата: jpg, jpeg, png, bmp, tiff, gif',
    )
