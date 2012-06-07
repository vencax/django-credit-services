'''
Created on Dec 29, 2011

@author: vencax
'''
from django.core.management.base import BaseCommand
import logging
from django.conf import settings
from django.contrib.auth.models import User
from valueladder.models import Thing
from django.template.loader import render_to_string
from django.utils.translation import ugettext
from django.contrib.sites.models import Site

class Command(BaseCommand):
    args = ''
    help = 'parses incoming mail and takes actions base on it'
    
    def handle(self, *args, **options):
        logging.basicConfig()
        _, _, data = args
        
        pMod = __import__(settings.CREDIT_NOTIFICATION_PARSER, globals={}, locals={})
        parser = pMod.Parser()
        vs, _, amount, _, currencyCode = parser.parse(data)
        
        currency = Thing.objects.get(code=currencyCode)
        try:
            self._processParsed(vs, amount, currency)
        except User.DoesNotExist:
            self._onBadVS(data)
            
    def _processParsed(self, vs, amount, currency):
        u = User.objects.get(pk=int(vs))
        companyInfo = u.companyinfo
        try:
            creditInfo = companyInfo.credits.get(currency=currency)
        except companyInfo.credits.model.DoesNotExist:
            creditInfo = companyInfo.credits.model(company=companyInfo, value=0,
                                                   currency=currency)
            
        creditInfo.value += amount
        creditInfo.save()
        
        if u.email:
            mailContent = render_to_string('creditservices/thxForCredit.html', {
                'amount' : amount,
                'currency' : currency,
                'state' : creditInfo.value,
                'domain' : Site.objects.get_current()
            })
            u.email_user(ugettext('credit increased'), mailContent)
        
    def _onBadVS(self, data):
        pass
        