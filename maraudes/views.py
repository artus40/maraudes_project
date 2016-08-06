import datetime
import calendar
from django.utils import timezone
from django.utils.functional import cached_property
from django.contrib import messages
from django.shortcuts import render, redirect
# Views
from django.views import generic
from website import views
# Models
from .models import (   Maraude, Maraudeur,
                        Rencontre, Lieu,
                        Planning,   )
from .compte_rendu import CompteRendu
# Forms
from django import forms
from django.forms import inlineformset_factory, modelformset_factory, modelform_factory
from django.forms.extras import widgets
from django_select2.forms import Select2Widget
from .forms import (    RencontreForm, RencontreInlineFormSet,
                        ObservationInlineFormSet, ObservationInlineFormSetNoExtra,
                        MaraudeAutoDateForm, MonthSelectForm,   )


class MaraudesView(views.WebsiteProtectedMixin):
    title = "Maraudes"
    header = "Maraudes"

    permissions = ['maraudes.view_maraudes']


class IndexView(MaraudesView, generic.TemplateView):
    header = "La Maraude"
    header_small = "Tableau de bord"

    template_name = "maraudes/index.html"
    count = 5
    @cached_property
    def dernieres_maraudes(self):
        """ Renvoie la liste des 'Maraude' passées et terminées """
        return Maraude.objects.get_past().filter(
                                            heure_fin__isnull=False
                                        ).order_by(
                                            '-date'
                                        )[:self.count]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['dernieres_maraudes'] = self.dernieres_maraudes
        return context

## MARAUDES

class MaraudeDetailsView(MaraudesView, generic.DetailView):
    model = Maraude
    context_object_name = "maraude"
    template_name = "maraudes/details.html"

    # Template
    header = "Maraude"
    header_small = "Celle-ci"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['compte_rendu'] = CompteRendu.objects.get(pk=self.object.pk)
        return context



class MaraudeListView(MaraudesView, generic.ListView):
    model = Maraude
    template_name = "maraudes/list.html"
    paginate_by = 10

    def get_queryset(self):
        today = datetime.date.today()
        return super().get_queryset().filter(
                                        date__lte=datetime.date.today()
                                    ).order_by('-date')


## COMPTE-RENDU DE MARAUDE

class CompteRenduCreateView(MaraudesView, generic.DetailView):
    model = Maraude
    template_name = "compte_rendu/compterendu_create.html"

    form = None
    inline_formset = None

    def get_forms(self, *args, initial=None):
        self.form = RencontreForm(*args,
                                  initial=initial)
        self.inline_formset = ObservationInlineFormSet(
                                *args,
                                instance=self.form.instance,
                                )

    def finalize(self):
        # TODO: check for errors to avoid last entry to be lost
        # Save 'heure_fin' on related Maraude object
        maraude = self.get_object()
        maraude.heure_fin = timezone.now()
        maraude.save()
        #TODO: send email to all Maraudeurs
        return redirect("maraudes:details",
                        pk=self.get_object().pk
                        )

    def post(self, request, *args, **kwargs):
        self.get_forms(request.POST, request.FILES)
        if self.form.has_changed():
            if not self.inline_formset.has_changed():
                if request.GET['finalize'] == "True":
                    return self.finalize()
                messages.warning(request, "Vous devez ajouter une observation !")
                return self.get(request, new_form=False)

            if not self.form.is_valid() or not self.inline_formset.is_valid():
                return self.get(request, new_form=False)
            rencontre = self.form.save(commit=False)
            rencontre.maraude = self.get_object()
            rencontre.save()
            self.inline_formset.save()

        return self.get(request, *args, **kwargs)

    def get(self, request, new_form=True, *args, **kwargs):
        try:
            if request.GET['finalize'] == "True":
                return self.finalize()
        except:
            pass

        def calculate_end_time(debut, duree):
            end_minute = debut.minute + duree
            hour = debut.hour + end_minute // 60
            minute = end_minute % 60
            return datetime.time(
                                hour,
                                minute,
                                debut.second
                        )
        if new_form:
            last_rencontre = self.get_object().rencontres.last()
            initial = None
            if last_rencontre:
                initial = {
                    'lieu': last_rencontre.lieu,
                    'heure_debut': calculate_end_time(
                                        last_rencontre.heure_debut,
                                        last_rencontre.duree),
                }
            self.get_forms(initial=initial)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form
        context['inline_formset'] = self.inline_formset
        context['rencontres'] = self.get_object().rencontres.order_by("-heure_debut")
        return context



class CompteRenduUpdateView(MaraudesView, generic.DetailView):
    """ Mettre à jour le compte-rendu de la maraude """
    model = Maraude
    context_object_name = "maraude"
    template_name = "compte_rendu/compterendu_update.html"

    base_formset = None
    inline_formsets = []
    rencontres_queryset = None
    forms = None

    def get_rencontres_queryset(self):
        return self.get_object().rencontres.all()

    def get_forms_with_inline(self, *args):
        self.base_formset = RencontreInlineFormSet(
                                    *args,
                                    instance=self.get_object(),
                                    prefix="rencontres"
                                    )

        self.inline_formsets = []
        for i, instance in enumerate(self.get_rencontres_queryset()):
            inline_formset = ObservationInlineFormSetNoExtra(
                    *args,
                    instance = instance,
                    prefix = "observation-%i" % i
                    )
            self.inline_formsets.append(inline_formset)

        # Aucun nouveau formulaire de 'Rencontre' n'est inclus.
        self.forms = [(self.base_formset[i], self.inline_formsets[i]) for i in range(len(self.inline_formsets))]

    def post(self, request, *args, **kwargs):
        self.get_forms_with_inline(request.POST, request.FILES)
        self.errors = False

        if self.base_formset.is_valid():
            for inline_formset in self.inline_formsets:
                if inline_formset.is_valid():
                    inline_formset.save()
            self.base_formset.save()
        else:
            self.errors = True

        if self.errors or request.GET['continue'] == "False": # Load page to display errors
            return self.get(request, *args, **kwargs)

        return redirect('maraudes:details', pk=self.get_object().pk)

    def get(self, request, *args, **kwargs):
        self.get_forms_with_inline()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['base_formset'] = self.base_formset
        context['forms'] = self.forms
        return context


## PLANNING

class PlanningView(MaraudesView, generic.TemplateView):
    """ Display and edit the planning of next Maraudes """

    template_name = "planning/planning.html"

    title = "Planning"
    header = "Plannification des maraudes"
    header_small = "Mois Année"

    def _parse_request(self):
        self.current_date = datetime.date.today()
        try:    self.month = int(self.request.GET['month'])
        except: self.month = self.current_date.month
        try:    self.year = int(self.request.GET['year'])
        except: self.year = self.current_date.year

    def _calculate_initials(self):
        self._parse_request()
        self.initials = []
        for day, time in Planning.get_maraudes_days_for_month(self.year, self.month):
            date = datetime.date(self.year, self.month, day)
            try:
                maraude = Maraude.objects.get(date=date)
            except Maraude.DoesNotExist:
                self.initials.append({
                        'date': date,
                        'heure_debut': time,
                        })

    def get_queryset(self):
        return Maraude.objects.filter(
                        date__month=self.month,
                        date__year=self.year,
                    )

    def get_formset(self, *args):
        self._calculate_initials()
        return modelformset_factory(
                            Maraude,
                            form = MaraudeAutoDateForm,
                            extra = len(self.initials),
                        )(
                            *args,
                            queryset = self.get_queryset(),
                            initial = self.initials
                        )

    def post(self, request):
        self.formset = self.get_formset(request.POST, request.FILES)
        for form in self.formset.forms:
            if form.is_valid():
                form.save()
        return redirect('maraudes:index')

    def get(self, request):
        self.formset = self.get_formset()
        return super().get(request)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['formset'] = self.formset
        context['select_form'] = MonthSelectForm(month=self.month, year=self.year)
        context['month'], context['year'] = self.month, self.year
        return context


## LIEU

class LieuCreateView(views.WebsiteProtectedWithAjaxMixin, generic.edit.CreateView):
    model = Lieu
    template_name = "maraudes/lieu_create.html"
    fields = "__all__"
    success_url = "/maraudes/"

    permissions = ['maraudes.add_lieu']

    def post(self, request, *args, **kwargs):
        if 'next' in self.request.POST:
            self.success_url = self.request.POST["next"]
        return super().post(self, request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['next'] = self.request.GET['next']
        except:
            context['next'] = None
        return context
