from django.db import models
from django.utils.translation import gettext_lazy as _
from invoices.models import CompanyInfo
from valueladder.models import Thing


class CreditInfo(models.Model):
    """
    Info about credit state (bilance) in certain units.
    """
    value = models.FloatField(_('value'))
    currency = models.ForeignKey(Thing)
    company = models.ForeignKey(CompanyInfo, related_name='credits')
