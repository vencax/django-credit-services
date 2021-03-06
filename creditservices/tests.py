from django.test import TestCase
from django.utils.translation import ugettext as _
from django.core.management import call_command
from django.core import mail
from invoices.models import Invoice, Item, CompanyInfo
from django.conf import settings
from django.contrib.auth.models import User
from creditservices.models import CreditChangeRecord
from valueladder.models import Thing
from creditservices.signals import processCredit


class InvoiceTest(TestCase):

    def setUp(self):
        TestCase.setUp(self)
        for i in range(settings.OUR_COMPANY_ID + 1):
            u = User(username='user%i' % i, last_name='Mr. %i' % i,
                     first_name='TJ', password='jfcisoa',
                     email='user%i@local.host' % i)
            u.save()
            CompanyInfo(town='town%i' % i, phone=(1000 + i), user=u).save()

    def testAccountNotification(self):
        """
        Test account notification command.
        """
        cInfo = self._chooseCompany()

        mail = 'P=F8=EDjem na kont=EC: 2400260986 =C8=E1stka: %i,00 VS: %i\
 Zpr=E1va p=F8=EDjemci: =20 Aktu=E1ln=ED z=F9statek: 20 144,82\
 Proti=FA=E8et: 321-2500109888/2010 SS:=1118 KS: 118'
        baseArgs = ('credit@vpn.vxk.cz', 'automat@fio.cz')

        amount = 433
        args = baseArgs + (
            mail % (amount, cInfo.user.id),
        )
        call_command('accountNotification', *args)

        try:
            CreditChangeRecord.objects.get(change=amount, company=cInfo)
        except CreditChangeRecord.DoesNotExist:
            raise AssertionError('CreditChangeRecord not exists')

        self._verifyOutMessage(to=[cInfo.user.email],
                               subject=_('credit increased'))
        self._verifyOutMessage(to=[cInfo.user.email],
                               subject=_('invoice'))

        try:
            i = Invoice.objects.get(subscriber=cInfo)
            Item.objects.get(invoice=i, price=amount)
        except Invoice.DoesNotExist:
            raise AssertionError('Invoice not generated')
        except Item.DoesNotExist:
            raise AssertionError('Bad invoice generated')

    def testProcessCredit(self):
        """
        Test account notification command.
        """
        cInfo = self._chooseCompany()
        currency = Thing.objects.get_default()
        amount = -4000
        contractor = CompanyInfo.objects.get_our_company_info()
        processCredit(cInfo, amount, currency, 'pokus', contractor.bankaccount)

        try:
            CreditChangeRecord.objects.get(change=amount, company=cInfo)
        except CreditChangeRecord.DoesNotExist:
            raise AssertionError('CreditChangeRecord not exists')

        self._verifyOutMessage(to=[cInfo.user.email],
                               subject=_('credit call'))

    def _verifyOutMessage(self, **kwargs):
        for m in mail.outbox:
            found = True
            for k, v in kwargs.items():
                if getattr(m, k) != v:
                    found = False
                    break

            if found:
                return
        raise AssertionError('Email with %s was not sent' % str(kwargs))

    def _chooseCompany(self):
        cInfos = CompanyInfo.objects.all().order_by('?')
        for c in cInfos:
            if c.id != settings.OUR_COMPANY_ID:
                return c
