from django.contrib import admin

from analyze.models import Doc, UserToDoc, Price, Cart

admin.site.register([Doc, UserToDoc, Price, Cart])