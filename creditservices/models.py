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
    
CompanyInfo.add_to_class('debtbegin', models.DateField(_('debt begin'), 
        blank=True, null=True, default=None,
        help_text=_('Date of cross zero in any of credits of the user')))
