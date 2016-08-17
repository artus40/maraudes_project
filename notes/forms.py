from .models import Note
from utilisateurs.models import Professionnel

from django import forms
from django.utils import timezone
from django_select2.forms import Select2Widget
from django.forms import Textarea



class NoteForm(forms.ModelForm):
    """ Generic Note form """
    class Meta:
        model = Note
        fields = ['sujet', 'text', 'created_by', 'created_date', 'created_time']
        widgets = {
            'sujet': Select2Widget(),
            'text': Textarea(attrs={'rows':4}),
        }



class SimpleNoteForm(forms.ModelForm):
    """ Simple note with only 'sujet' and 'text' fields.

        Usefull with children of 'Note' that defines all 'note_*'
        special methods.
    """
    class Meta(NoteForm.Meta):
        fields = ['sujet', 'text']



class UserNoteForm(NoteForm):
    """ Form that sets 'created_by' with current user id.
        This requires 'request' object at initialization
    """
    class Meta(NoteForm.Meta):
        fields = ['sujet', 'text', 'created_date', 'created_time']

    def __init__(self, request, **kwargs):
        args = []
        if request.POST:
            args += (request.POST, request.FILES)
        super().__init__(*args, **kwargs)
        try:
            self.author = Professionnel.objects.get(pk=request.user.pk)
        except Professionnel.DoesNotExist:
            msg = "%s should not have been initiated with '%s' user" % (self, request.user)
            raise RuntimeError(msg)

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.created_by = self.author
        if commit:
            instance.save()
        return instance

class UserAutoDateNoteForm(UserNoteForm):
    """ Form that automatically sets 'date' and 'time' to save time """

    class Meta(UserNoteForm.Meta):
        fields = ['sujet', 'text']

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.created_date = timezone.now().date()
        instance.created_time = timezone.now().time()
        if commit:
            instance.save()
        return instance

class AutoNoteForm(UserAutoDateNoteForm):
    class Meta(UserAutoDateNoteForm.Meta):
        fields = ['text']

    def __init__(self, request, **kwargs):
        self.sujet = kwargs.pop('sujet')
        super().__init__(request, **kwargs)

    def save(self, commit=True):
        print('Saving : ', self, 'with', self.sujet)
        inst = super().save(commit=False)
        inst.sujet = self.sujet
        if commit:
            inst.save()
        return inst
