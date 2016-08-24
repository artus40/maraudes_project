from django.views.generic.edit import FormMixin

from .forms import *

class NoteFormMixin(FormMixin):

    form_class = None

    forms = None

    def get_form(self, prefix, form_class=None):
        # Should add test to ensure this instance class is
        # has SingleObjectMixin set with Sujet model ??
        kwargs = self.get_form_kwargs()
        kwargs['prefix'] = prefix
        if not form_class:
            form_class = self.forms[prefix]
        try:
            form = form_class(
                        **kwargs
                        )
        except TypeError: #Forms that requires request
            form = form_class(
                        self.request,
                        **kwargs
                        )
        return form

    def post(self, request, **kwargs):
        for prefix in self.forms.keys():
            form = self.get_form(prefix)
            if form.is_valid():
                form.save()
                return self.form_valid(form)
        return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super(FormMixin, self).get_context_data(**kwargs)
        for prefix in self.forms.keys():
            context['%s_form' % prefix] = self.get_form(prefix)
        return context

