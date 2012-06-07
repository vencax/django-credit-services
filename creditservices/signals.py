'''
Created on May 30, 2012

@author: vencax
'''
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from django.utils.translation import ugettext

def invoice_saved(instance, sender, **kwargs):
    """
    Called on invoice save.
    It adds invoice value to user's credit and generate
    margin call if necessary.
    """
    if not instance.paymentWay != instance.PREPAID:
        return
    if len(instance.items.all()) > 0 and not instance.paid:
        companyInfo = instance.subscriber
        try:
            creditInfo = companyInfo.credits.get(currency=instance.currency)
        except companyInfo.credits.model.DoesNotExist:
            creditInfo = companyInfo.credits.model(company=companyInfo, value=0,
                                                   currency=instance.currency)
        if instance.typee == 'i':
            creditInfo.value += instance.totalPrice()
        elif instance.typee == 'o':
            creditInfo.value -= instance.totalPrice()
                    
        creditInfo.save()
        instance.paid = True
        instance.save()
        
        if creditInfo.value < settings.CREDIT_MINIMUM:
            mailContent = render_to_string('creditservices/marginCall.html', {
                'currency' : instance.currency,
                'state' : creditInfo.value,
                'domain' : Site.objects.get_current(),
                'user' : companyInfo.user,
                'account' : instance.contractor.bankaccount
            })
            companyInfo.user.email_user(ugettext('credit call'), mailContent)
    
def invoice_deleted(instance, sender, **kwargs):
    #TODO: reverse credit from this invoice
    pass