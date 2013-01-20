
from django.conf import settings
from django.views.generic.base import TemplateView
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from invoices.models import CompanyInfo

from .models import CreditChangeRecord


class InfoView(TemplateView):
    template_name = 'creditservices/info.html'

    def dispatch(self, request, *args, **kwargs):
        if getattr(settings, 'CREDIT_VIEW_NEED_LOGIN', False):
            return login_required(super(InfoView, self).dispatch)
        else:
            return super(InfoView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        changeRecords = CreditChangeRecord.objects.\
            filter(company=self.company)

        return {
            'credRecords': changeRecords,
            'company': self.company
        }

    def get(self, request, *args, **kwargs):
        self.company = get_object_or_404(CompanyInfo, user_id=kwargs['uid'])
        return super(InfoView, self).get(request, *args, **kwargs)
