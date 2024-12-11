from django.shortcuts import render
from django.views.generic import DetailView, TemplateView

from c3ds.core.models import BaseView


# Create your views here.
class TestView(TemplateView):
    template_name = 'core/test.html'

class GenericView(DetailView):
    model = BaseView
    context_object_name = 'view'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        return obj.get_specific()

    def get_template_names(self):
        return [self.object.get_template_name()]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            'layout_mode': getattr(self.object, 'layout_mode', 'normal')
        })
        return ctx
