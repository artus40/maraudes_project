from django.views.generic.edit import FormMixin
from django.contrib import messages

from .forms import *

class NoteFormMixin(FormMixin):

    forms = None

    def get_form(self, prefix):
        kwargs = self.get_form_kwargs()
        kwargs['prefix'] = prefix
        kwargs['request'] = self.request
        form_class = self.forms[prefix]
        return form_class(**kwargs)

    def post(self, request, **kwargs):
        for prefix in self.forms.keys():
            form = self.get_form(prefix)
            if form.is_valid():
                form.save()
                return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        messages.success(self.request, "Un nouveau %s a été enregistré" % form.prefix)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(FormMixin, self).get_context_data(**kwargs)
        for prefix in self.forms.keys():
            context['%s_form' % prefix] = self.get_form(prefix)
        return context

