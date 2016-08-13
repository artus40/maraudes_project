from .models import Note
from django import forms
from django.utils import timezone
from django_select2.forms import Select2Widget
from django.forms import Textarea

class NoteForm(forms.ModelForm):

    class Meta:
        model = Note
        fields = ['sujet', 'text']
        widgets = {
            'sujet': Select2Widget(),
            'text': Textarea(attrs={'rows':4}),
        }

    def save(self, *args, **kwargs):
        # Get data for extra fields of Note

        return super().save(*args, **kwargs)


class UserNoteForm(forms.ModelForm):

    class Meta:
        model = Note
        fields = ['sujet', 'text', 'created_date', 'created_time']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.created_by = None #TODO: Get user with needed Class
        if commit:
            instance.save()
        return instance

class NoteAutoDateForm(UserNoteForm):

    class Meta(UserNoteForm.Meta):
        model = Note
        fields = ['text']
        widgets = {
            'text': Textarea(attrs={'rows':4, 'placeholder': "Texte"}),
        }

    def __init__(self, request, **kwargs):
        self.sujet = kwargs.pop('sujet')
        self.pk = kwargs.pop('pk')
        self.user = request.user
        args = []
        if request.POST:
            args = (request.POST, request.FILES)
        super().__init__(*args)

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.sujet = self.sujet
        instance.created_date = timezone.now().date()
        instance.created_time = timezone.now().time()
        if commit:
            instance.save()
        return instance


