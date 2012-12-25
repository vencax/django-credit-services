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
from creditservices.signals import new_credit_arrived, processCredit
from django.core.mail import mail_admins


class Command(EmailHandlingCommand):
    help = 'parses incoming mail and \
takes actions base on it'  # @ReservedAssignment

    def processMail(self, recipient, mailfrom, data):
        activate(settings.LANGUAGE_CODE)

        logging.info('Loading %s' % settings.CREDIT_NOTIFICATION_PARSER)

        pMod = __import__(settings.CREDIT_NOTIFICATION_PARSER,
                          globals={}, locals={}, fromlist=['Parser'])
        try:
            parser = pMod.Parser()
            parsed = parser.parse(data)

            logging.info('Parsed: %s' % str(parsed))

            transactionType, vs, ss, amount, _, _, currencyCode = parsed

            if transactionType != 'IN':
                return

            currency = Thing.objects.get(code=currencyCode)

            self._processParsed(vs, ss, amount, currency)
        except Exception, e:
            logging.exception(e)
            self._onBadVS(data)

    def _processParsed(self, vs, ss, amount, currency):
        u = User.objects.get(pk=int(vs))
        companyInfo = CompanyInfo.objects.get(user__id=u.id)

        processCredit(companyInfo, amount, currency,
                      ugettext('income payment'))

        self._resetDebtFlag(companyInfo)

        new_credit_arrived.send(sender=CompanyInfo, vs=vs, ss=ss,
                                amount=amount, currency=currency)

        if u.email:
            mailContent = render_to_string(
                'creditservices/thxForCredit.html', {
                'amount': amount,
                'currency': currency,
                'state': u.getCurrentCredit(currency),
                'domain': Site.objects.get_current()
            })
            u.email_user(ugettext('credit increased'), mailContent)

    def _onBadVS(self, data):
        mail_admins('Unassotiated payment', data, fail_silently=True)

    def _resetDebtFlag(self, companyInfo):
        """
        If company has now all it credits positive, reset debtbegin flag
        """
        if companyInfo.debtbegin is not None:
            creds = {}
            for crc in companyInfo.user.changeRecords.all():
                if crc.currency not in creds:
                    creds[crc.currency] = 0
                creds[crc.currency] += crc.change
            for val in creds.values():
                if val < 0:
                    return
            companyInfo.debtbegin = None
            companyInfo.save()
