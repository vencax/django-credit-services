'''
Created on Jun 7, 2012

@author: vencax
'''
from django.contrib import admin

from .models import CreditChangeRecord


class CreditChangeRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'change', 'currency', 'increase', 'date')
    list_filter = ('currency', 'increase')
    search_fields = ('user__username', 'change')

admin.site.register(CreditChangeRecord, CreditChangeRecordAdmin)
