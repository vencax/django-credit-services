from django.test import TestCase
from django.core.management import call_command
from invoices.models import Invoice, CompanyInfo
from django.conf import settings
from django.contrib.auth.models import User
from creditservices.models import CreditChangeRecord


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
        cInfos = CompanyInfo.objects.all().order_by('?')
        for c in cInfos:
            if c.id != settings.OUR_COMPANY_ID:
                cInfo = c

        mail = 'P=F8=EDjem na kont=EC: 2400260986 =C8=E1stka: %i,00 VS: %i\
 Zpr=E1va p=F8=EDjemci: =20 Aktu=E1ln=ED z=F9statek: 20 144,82\
 Proti=FA=E8et: 321-2500109888/2010 SS:=118 KS: 0008'
        baseArgs = ('credit@vpn.vxk.cz', 'automat@fio.cz')

        amount = 433
        args = baseArgs + (
            mail % (amount, cInfo.id),
        )
        call_command('accountNotification', *args)

        try:
            CreditChangeRecord.objects.get(change=amount, company=cInfo)
        except CreditChangeRecord.DoesNotExist:
            raise AssertionError('CreditChangeRecord not exists')

        try:
            Invoice.objects.get(subscriber=cInfo)
        except Invoice.DoesNotExist:
            raise AssertionError('Invoice not generated')
