'''
Created on Dec 29, 2011

@author: vencax
'''
import logging
from django.conf import settings
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.utils.translation import activate
from django.utils.translation import ugettext
from django.contrib.sites.models import Site
from mailserver.command import EmailHandlingCommand
from valueladder.models import Thing
from invoices.models import CompanyInfo

class Command(EmailHandlingCommand):
    help = 'parses incoming mail and takes actions base on it'
    
    def processMail(self, recipient, mailfrom, data):
        activate(settings.LANGUAGE_CODE)
        
        logging.info('Loading %s' % settings.CREDIT_NOTIFICATION_PARSER)
        
        pMod = __import__(settings.CREDIT_NOTIFICATION_PARSER, 
                          globals={}, locals={}, fromlist=['Parser'])
        parser = pMod.Parser()
        parsed = parser.parse(data)
        
        logging.info('Parsed: %s' % str(parsed))
        
        vs, ss, amount, _, currencyCode = parsed
        
        currency = Thing.objects.get(code=currencyCode)
        try:
            self._processParsed(vs, ss, amount, currency)
        except User.DoesNotExist:
            self._onBadVS(data)
        except CompanyInfo.DoesNotExist:
            self._onBadVS(data)
            
    def _processParsed(self, vs, ss, amount, currency):
        u = User.objects.get(pk=int(vs))
        companyInfo = CompanyInfo.objects.get(user__id=u.id)
        try:
            creditInfo = companyInfo.credits.get(currency=currency)
        except companyInfo.credits.model.DoesNotExist:
            creditInfo = companyInfo.credits.model(company=companyInfo, value=0,
                                                   currency=currency)
        
        creditInfo.value += amount
        creditInfo.save()
        
        # run appropriate credit handlers
        try:
            handler = self._getHandler(settings.CREDIT_HANDLERS[ss])            
        except KeyError:
            handler = self._getHandler(settings.CREDIT_HANDLERS[None])
        handler(companyInfo, vs, amount, currency)
        
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

    def _getHandler(self, handler):
        parts = handler.split('.')
        func = parts[len(parts)-1]
        module = __import__('.'.join(parts[:len(parts)-1]), 
                            globals={}, locals={}, 
                            fromlist=[func])
        return getattr(module, func)
        