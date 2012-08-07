from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from invoices.models import CompanyInfo
from valueladder.models import Thing

class CreditInfo(models.Model):
    """
    Info about credit state (bilance) in certain units.
    """
    value = models.FloatField(_('value'))
    currency = models.ForeignKey(Thing)
    company = models.ForeignKey(CompanyInfo, related_name='credits')
    
    class Meta:
        verbose_name = _('credit info')
        verbose_name_plural = _('credit infos')
        ordering = ['company']
        
class CreditChangeRecord(models.Model):
    """
    Record how a credit changes in time.
    """
    change = models.FloatField(_('change'))
    increase = models.BooleanField(_('increase'))
    currency = models.ForeignKey(Thing)
    user = models.ForeignKey(User, related_name='credits')
    date = models.DateField(verbose_name=_('date'), editable=False, 
                            auto_now_add=True)
    detail = models.TextField(_('detail'), max_length=512)
    
    class Meta:
        verbose_name = _('credit change record')
        verbose_name_plural = _('credit change records')
        ordering = ['date']
    
CompanyInfo.add_to_class('debtbegin', models.DateField(_('debt begin'), 
        blank=True, null=True, default=None, editable=False,
        help_text=_('Date of cross zero in any of credits of the user')))