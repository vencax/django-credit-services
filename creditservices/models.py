from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save, post_delete
from invoices.models import CompanyInfo, Invoice
from valueladder.models import Thing

from .signals import invoice_saved, invoice_deleted

class CreditInfo(models.Model):
    """
    Info about credit state (bilance) in certain units.
    """
    value = models.FloatField(_('value'))
    currency = models.ForeignKey(Thing)
    company = models.ForeignKey(CompanyInfo, related_name='credits')

Invoice.add_to_class('prepaid', models.BooleanField(_('prepaid'), default=False))

post_save.connect(invoice_saved, sender=Invoice,
                  dispatch_uid='invoice_save_credit')
post_delete.connect(invoice_deleted, sender=Invoice,
                    dispatch_uid='invoice_delete_credit')