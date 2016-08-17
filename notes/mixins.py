from django.views.generic.edit import FormMixin, ProcessFormView
from django.shortcuts import redirect

from .forms import *

class SujetNoteFormMixin(object):

    form_class = AutoNoteForm

    def get_form(self, request, **kwargs):
        # Should add test to ensure this instance class is
        # has SingleObjectMixin set with Sujet model ??
        return self.form_class(
                        self.request,
                        sujet=self.get_object()
                        )

    def dispatch(self, request, **kwargs):
        self.form = self.get_form(request)
        return super().dispatch(request, **kwargs)

    def post(self, request, **kwargs):
        if self.form.is_valid():
            self.form.save()
            return redirect(self.get_success_url())
        return self.get(request, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['note_form'] = self.form
        return context

