'''
Created on May 30, 2012

@author: vencax
'''
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from django.utils.translation import ugettext
from django.dispatch.dispatcher import Signal


CREDIT_MINIMUM = getattr(settings, 'CREDIT_MINIMUM', 0)
#def invoice_saved(instance, sender, **kwargs):
#    """
#    Called on invoice save.
#    It adds invoice value to user's credit and generate
#    margin call if necessary.
#    """
#    if instance.typ != instance.PREPAID:
#        return
#    if len(instance.items.all()) > 0 and not instance.paid:
#        if instance.direction == 'i':
#            value = instance.totalPrice()
#        elif instance.direction == 'o':
#            value = -instance.totalPrice()
#
#        processCredit(instance, instance.contractor.bankaccount)
#
#        instance.paid = True
#        instance.save()
#
#def invoice_deleted(instance, sender, **kwargs):
#    #TODO: reverse credit from this invoice
#    pass

shutdown_credit_services = Signal(
    providing_args=['instance']
)
new_credit_arrived = Signal(
    providing_args=['companyInfo', 'currency', 'amount']
)

CREDIT_SYMBOL = getattr(settings, 'CREDIT_SYMBOL', 118)


def on_account_change(sender, parsed, **kwargs):
    """
    Handle incoming credit increase transfer notification.
    """
    amount = parsed['amount']
    if parsed['constSymb'] != CREDIT_SYMBOL or amount <= 0:
        return

    from creditservices.models import CompanyInfo
    from invoices.models import BadIncommingTransfer

    try:
        companyInfo = CompanyInfo.objects.get(user_id=parsed['varSymb'])
    except CompanyInfo.DoesNotExist:
        BadIncommingTransfer(invoice=None,
            typee='u', transactionInfo=str(kwargs))

    from valueladder.models import Thing
    currency = Thing.objects.get(code=parsed['currency'])
    processCredit(companyInfo, amount, currency, ugettext('income payment'))

    _resetDebtFlag(companyInfo)

    new_credit_arrived.send(sender=CompanyInfo, companyInfo=companyInfo,
                            amount=amount, currency=currency)

    _sendThanksForCredit(companyInfo, amount, currency)
    return 'credit processed'


def processCredit(companyInfo, value, currency, details, bankaccount=None):
    """ Adds value of appropriate creditInfo.
        Saves CreditChangeRecord.
        Sends margin call if necessary. """
    if companyInfo.user_id == settings.OUR_COMPANY_ID:
        return  # do not account ourself

    from .models import CreditChangeRecord
    CreditChangeRecord(company=companyInfo, change=value,
                       increase=value > 0,
                       currency=currency,
                       detail=details[:512]).save()

    currentCredit = companyInfo.getCurrentCredit(currency)

    if value < 0 and currentCredit < CREDIT_MINIMUM:
        if bankaccount is None:
            bankaccount = companyInfo._default_manager.model.objects.\
                            get_our_company_info().bankaccount
        mailContent = render_to_string('creditservices/marginCall.html', {
            'currency': currency,
            'state': currentCredit,
            'domain': Site.objects.get_current(),
            'company': companyInfo,
            'account': bankaccount,
            'specSymbol': CREDIT_SYMBOL
        })
        companyInfo.user.email_user(ugettext('credit call'), mailContent)

    return currentCredit


def _resetDebtFlag(companyInfo):
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


def _sendThanksForCredit(companyInfo, amount, currency):
    if companyInfo.user.email:
        mailContent = render_to_string(
            'creditservices/thxForCredit.html', {
            'amount': amount,
            'currency': currency,
            'state': companyInfo.getCurrentCredit(currency),
            'domain': Site.objects.get_current(),
        })
        companyInfo.user.email_user(ugettext('credit increased'), mailContent)
