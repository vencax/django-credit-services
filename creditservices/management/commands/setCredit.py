'''
Created on Dec 29, 2011

@author: vencax
'''
import logging
from invoices.models import CompanyInfo
from django.core.management.base import BaseCommand
from valueladder.models import Thing
from creditservices.signals import processCredit
from optparse import make_option
from django.utils.translation import activate
from django.conf import settings

class Command(BaseCommand):
    help = 'check credits of companies if they are not in debt too long' #@ReservedAssignment
    
    option_list = BaseCommand.option_list + (
        make_option('--user', help='ID of user that the credit has to be set to'),
        make_option('--value', help='new credit value'),
        make_option('--currency', help='currency code'),
    )
    
    def handle(self, *args, **options):
        activate(settings.LANGUAGE_CODE)
        logging.basicConfig()
        companyInfo = CompanyInfo.objects.get(user__id=options['user'])
        if options['currency']:
            currency = Thing.objects.get(code=options['currency'])
        else:
            currency = Thing.objects.get_default()
        bankAccount = CompanyInfo.objects.get_our_company_info().bankaccount
        
        processCredit(companyInfo, int(options['value']), 
                      currency, bankAccount, 'manual set credit')