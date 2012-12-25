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
from django.utils.translation import activate


class Command(BaseCommand):
    help = 'check credits of companies \
if they are not in debt too long'  # @ReservedAssignment

    DEPTH_DEATHLINE = getattr(settings, 'DEPTH_DEATHLINE', 30)

    def handle(self, *args, **options):
        activate(settings.LANGUAGE_CODE)
        logging.basicConfig()

        for companyInfo in CompanyInfo.objects.all():
            self._processCredit(companyInfo)

    @commit_on_success
    def _processCredit(self, companyInfo):
        # start count days in debt
        if self._hasUserDept(companyInfo.user) and \
        companyInfo.debtbegin is None:
            companyInfo.debtbegin = datetime.date.today()
            companyInfo.save()

        # check if the company is not in debt too long
        elif companyInfo.debtbegin is not None:
            daysInDept = (datetime.date.today() - companyInfo.debtbegin).days
            if daysInDept > self.DEPTH_DEATHLINE:
                shutdown_credit_services.send(sender=CompanyInfo,
                                              instance=companyInfo)

    def _hasUserDept(self, user):
        creds = {}
        for crc in user.changeRecords.all():
            if crc.currency not in creds:
                creds[crc.currency] = 0
            creds[crc.currency] += crc.change
        for val in creds.values():
            if val < 0:
                return True
        return False
