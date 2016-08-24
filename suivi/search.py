from django.views.generic.edit import FormMixin, ProcessFormView
from django import forms

from django.shortcuts import redirect

class SearchForm(forms.Form):

    search_text = forms.CharField(64, widget=forms.widgets.TextInput(attrs={'placeholder':"NotYetImplemented"}))

    def __init__(self, *args, **kwargs):
        kwargs['prefix'] = 'search'
        return super().__init__(*args, **kwargs)

    def clean(self):
        super().clean()
        #Do search and store result
        self.result = None

    def is_valid(self):
        valid = super().is_valid()
        if not self.result:
            return False
        return valid

class SearchFormMixin(FormMixin):
    """ Add 'search_form' to context.
        Made compatible with NoteFormMixin using 'prefix' argument in get_form
    """
    def get_form(self, prefix):
        if prefix == 'search':
            return SearchForm()
        return super().get_form(prefix)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = self.get_form('search')
        return context

""" What to do ?

- We shall use 'django-watson', need to install it

- Create view to parse search_form data then redirect
- Link form in menu_sujets to this view
"""

class SearchFormProcessView(ProcessFormView):
    pass
