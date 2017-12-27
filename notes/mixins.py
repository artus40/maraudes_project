from django.views.generic.edit import FormMixin
from django.contrib import messages


class NoteFormMixin(FormMixin):
    """ A mixin that allows to easily embed multiple distinct forms on a view.
        Only one form can be processed by request !
    """

    # 'forms' shall be a dict of form classes, indexed by a prefix
    forms = None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_form_by_prefix(self, prefix):
        try:
            return self.get_form(form_class=self.forms[prefix])
        except KeyError:
            raise ValueError("The form with prefix %s is not declared in %s" % (prefix, self.forms))

    def post(self, request, **kwargs):
        """ Save the first valid form found or reload page displaying a warning """
        for prefix in self.forms.keys():
            form = self.get_form_by_prefix(prefix)
            if form.is_valid():
                form.save()
                messages.success(self.request, "Un nouveau %s a été enregistré" % prefix)
                return self.form_valid(form)
        messages.warning(request, "Il y a eu une erreur lors du traitement du formulaire")
        return self.get(request, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(FormMixin, self).get_context_data(**kwargs)
        for prefix in self.forms.keys():
            context['%s_form' % prefix] = self.get_form_by_prefix(prefix)
        return context
