'''
Created on Dec 29, 2011

@author: vencax
'''
import logging
import datetime
from django.conf import settings
from invoices.models import CompanyInfo
from django.core.management.base import BaseCommand
from creditservices.signals import shutdown_credit_services
from django.db.transaction import commit_on_success

class Command(BaseCommand):
    help = 'check credits of companies if they are not in debt too long' #@ReservedAssignment
    DEPTH_DEATHLINE = getattr(settings, 'DEPTH_DEATHLINE', 30)
    
    def handle(self, *args, **options):
        logging.basicConfig()
        
        for companyInfo in CompanyInfo.objects.all():
            for creditInfo in companyInfo.credits.all():
                self._processCredit(companyInfo, creditInfo)

    @commit_on_success
    def _processCredit(self, companyInfo, creditInfo):
        # start count days in debt
        if creditInfo.value and companyInfo.debtbegin is None:
            companyInfo.debtbegin = datetime.datetime.now()
            companyInfo.save()
    
        # check if the company is not in debt too long
        daysInDept = (datetime.date.today() - companyInfo.debtbegin).days
        if daysInDept > self.DEPTH_DEATHLINE:
            shutdown_credit_services.send(sender=CompanyInfo,
                                          instance=companyInfo,
                                          creditInfo=creditInfo)