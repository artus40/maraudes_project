
from .forms import NoteAutoDateForm

class NoteFormMixin(object):

    form = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_class = NoteAutoDateForm


    def dispatch(self, request, **kwargs):
        self.form = self.get_form(request, **kwargs)
        return super().dispatch(request, **kwargs)

    def post(self, request, **kwargs):
        print('post:', self.form)
        if self.form.is_valid():
            self.form.save()
        return self.get(request, **kwargs)

    def get_form(self, request, **kwargs):
        kwargs['sujet'] = self.get_object()
        return NoteAutoDateForm(
                        request,
                        **kwargs
                        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['note_form'] = self.form
        return context
