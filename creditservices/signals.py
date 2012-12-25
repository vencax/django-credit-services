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
    providing_args=['currency', 'vs', 'ss', 'amount']
)


def processCredit(companyInfo, value, currency, details, bankaccount=None):
    """ Adds value of appropriate creditInfo.
        Saves CreditChangeRecord.
        Sends margin call if necessary. """
    if companyInfo.user_id == settings.OUR_COMPANY_ID:
        return  # do not account ourself

    from .models import CreditChangeRecord
    CreditChangeRecord(user=companyInfo.user, change=value,
                       increase=value > 0,
                       currency=currency,
                       detail=details[:512]).save()

    if value < 0 and \
    companyInfo.user.getCurrentCredit(currency) < CREDIT_MINIMUM:
        if bankaccount is None:
            bankaccount = companyInfo._default_manager.model.objects.\
                            get_our_company_info().bankaccount
        mailContent = render_to_string('creditservices/marginCall.html', {
            'currency': currency,
            'state': companyInfo.user.currentCredit.value,
            'domain': Site.objects.get_current(),
            'company': companyInfo,
            'account': bankaccount
        })
        companyInfo.user.email_user(ugettext('credit call'), mailContent)
