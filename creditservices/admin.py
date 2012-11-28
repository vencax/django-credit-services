'''
Created on Jun 7, 2012

@author: vencax
'''
from django.contrib import admin

from .models import CreditInfo, CreditChangeRecord


class CreditInfoAdmin(admin.ModelAdmin):
    list_display = ('company', 'value', 'currency')
    list_filter = ('currency', )
    search_fields = ('company', 'value')
    readonly_fields = ('company', 'currency')

admin.site.register(CreditInfo, CreditInfoAdmin)


class CreditChangeRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'change', 'currency', 'increase', 'date')
    list_filter = ('currency', 'increase')
    search_fields = ('user__username', 'change')

admin.site.register(CreditChangeRecord, CreditChangeRecordAdmin)
