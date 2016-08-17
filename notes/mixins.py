from django.views.generic.edit import FormMixin, ProcessFormView
from django.shortcuts import redirect

from .forms import *

class NoteFormMixin(FormMixin):

    form_class = None

    def get_form(self):
        # Should add test to ensure this instance class is
        # has SingleObjectMixin set with Sujet model ??
        kwargs = self.get_form_kwargs()
        return self.form_class(
                        self.request,
                        **kwargs
                        )

    def post(self, request, **kwargs):
        form = self.get_form()
        if form.is_valid():
            form.save()
            return self.form_valid(form)
        return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['note_form'] = self.get_form()
        return context

