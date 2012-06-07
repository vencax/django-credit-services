'''
Created on Jun 7, 2012

@author: vencax
'''
from django.contrib import admin
#from invoices.admin import CompanyInfoAdmin

from .models import CreditInfo

class CreditInfoAdmin(admin.TabularInline):
    model = CreditInfo
    extra = 1
    
#CompanyInfoAdmin.inlines.append(CreditInfoAdmin)