'''
Created on Jun 7, 2012

@author: vencax
'''
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import CreditChangeRecord


def companyUser(self):
    return self.company.user
companyUser.short_description = _('username')


class CreditChangeRecordAdmin(admin.ModelAdmin):
    list_display = (companyUser, 'change', 'currency', 'increase', 'date')
    list_filter = ('currency', 'increase')
    search_fields = ('company__user__username', 'change', 'company__phone')

admin.site.register(CreditChangeRecord, CreditChangeRecordAdmin)
