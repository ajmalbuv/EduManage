from rest_framework.authtoken.models import TokenProxy

from django.contrib import admin
from django.contrib.auth.models import Group

admin.site.unregister(Group)
admin.site.unregister(TokenProxy)
