# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.admin import AdminSite
from home_finance.components.external_account.models import ExternalAccount
from django.contrib import admin


class MyAdminSite(AdminSite):
    site_header = 'Home Finance Project'

class ExternalAccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'interest_rate', 'notes')

admin_site = MyAdminSite(name='myadmin')
admin_site.register(ExternalAccount, ExternalAccountAdmin)
