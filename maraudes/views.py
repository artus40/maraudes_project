import datetime
import calendar
import logging

logger = logging.getLogger(__name__)

from django.utils import timezone
from django.shortcuts import redirect
from django.views import generic
from django.core.mail import send_mail
from django.forms import modelformset_factory

from utilisateurs.mixins import MaraudeurMixin
# Models
from .models import (   Maraude, Maraudeur,
                        Rencontre, Lieu,
                        Planning,   )
from .compte_rendu import CompteRendu
# Forms
from .forms import (    RencontreForm,
                        ObservationInlineFormSet,
                        MaraudeHiddenDateForm, MonthSelectForm,
                        AppelForm, SignalementForm   )
from notes.mixins import NoteFormMixin


def derniers_sujets_rencontres():
    """ Renvoie le 'set' des sujets rencontrés dans les deux dernières maraudes """
    sujets = set()
    for cr in list(CompteRendu.objects.filter(heure_fin__isnull=False))[-2:]:
        for obs in cr.get_observations():
            sujets.add(obs.sujet)
    return list(sujets)



class IndexView(NoteFormMixin, MaraudeurMixin, generic.TemplateView):

    template_name = "maraudes/index.html"

    #NoteFormMixin
    forms = {
        'appel': AppelForm,
        'signalement': SignalementForm,
    }

    def get_initial(self):
        now = timezone.localtime(timezone.now())
        return {'created_date': now.date(),
                'created_time': now.time()}

    def get_success_url(self):
        return reverse('suivi:index')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['prochaine_maraude'] = Maraude.objects.get_next_of(self.request.user)
        context['derniers_sujets_rencontres'] = derniers_sujets_rencontres()

        if self.request.user.is_superuser:
            context['missing_cr'] = CompteRendu.objects.get_queryset().filter(
                    heure_fin__isnull=True,
                    date__lte = timezone.localtime(timezone.now()).date()
                )
        return context



## COMPTE-RENDU DE MARAUDE

class CompteRenduCreateView(MaraudeurMixin, generic.DetailView):
    """ Vue pour la création d'un compte-rendu de maraude """

    model = CompteRendu
    template_name = "maraudes/compterendu.html"
    context_object_name = "maraude"

    form = None
    inline_formset = None

    def get_forms(self, *args, initial=None):
        self.form = RencontreForm(*args,
                                  initial=initial)
        self.inline_formset = ObservationInlineFormSet(
                                    *args,
                                    instance=self.form.instance
                                )

    def finalize(self):
        print('finalize !')
        maraude = self.get_object()
        maraude.heure_fin = timezone.now()
        maraude.save()
        # Redirect to a new view to edit mail ??
        # Add text to some mails ? Transmission, message à un référent, etc...
        # Send mail to Maraudeurs
        _from = maraude.referent.email
        # Shall select only Maraudeur where 'is_active' is True !
        recipients = [m for m in Maraudeur.objects.all() if m not in (maraude.referent, maraude.binome)]
        objet = "Compte-rendu de maraude : %s" % maraude.date
        message = "Sujets rencontrés : ..." #TODO: Mail content
        send_mail(objet, message, _from, recipients)

        return redirect("notes:details-maraude",
                        pk=maraude.pk
                        )

    def post(self, request, *args, **kwargs):
        self.get_forms(request.POST, request.FILES)
        if self.form.has_changed():
            if not self.form.is_valid() or not self.inline_formset.is_valid():
                return self.get(request, new_form=False)
            rencontre = self.form.save(commit=False)
            rencontre.maraude = self.get_object()
            rencontre.save()
            self.inline_formset.save()

        return redirect('maraudes:create', pk=self.get_object().pk)

    def get(self, request, new_form=True, *args, **kwargs):
        if request.GET.get('finalize', False) == "True":
            return self.finalize()

        def calculate_end_time(debut, duree):
            end_minute = debut.minute + duree
            hour = debut.hour + end_minute // 60
            if hour >= 24: hour -= 24
            elif hour < 0: hour += 24
            minute = end_minute % 60
            return datetime.time(
                                hour,
                                minute,
                                0
                        )
        if new_form:
            last_rencontre = self.get_object().rencontres.last()
            if last_rencontre:
                initial = {
                    'lieu': last_rencontre.lieu,
                    'heure_debut': calculate_end_time(
                                        last_rencontre.heure_debut,
                                        last_rencontre.duree),
                }
            else:
                initial = {
                    'heure_debut': self.get_object().heure_debut
                }
            self.get_forms(initial=initial)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form
        context['inline_formset'] = self.inline_formset
        context['rencontres'] = self.get_object().rencontres.order_by("-heure_debut")
        return context



class PlanningView(MaraudeurMixin, generic.TemplateView):
    """ Vue d'édition du planning des maraudes """

    template_name = "maraudes/planning.html"

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
                            form = MaraudeHiddenDateForm,
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
            else:
                logger.info("Form was ignored ! (%s)" % (form.errors.as_data()))
        return redirect('maraudes:index')

    def get(self, request):
        self.formset = self.get_formset()
        return super().get(request)

    def get_weeks(self):
        """ List of (day, form) tuples, split by weeks """

        def form_generator(forms):
            """ Yields None until the generator receives the day of
                next form.
            """
            forms = iter(sorted(forms, key=lambda f: f.initial['date']))
            day = yield
            for form in forms:
                while day != form.initial['date'].day:
                    day = yield None
                day = yield form

            while True: # Avoid StopIteration
                day = yield None

        form_or_none = form_generator(self.formset)
        form_or_none.send(None)

        return [
                [(day, form_or_none.send(day)) for day in week]
                for week in calendar.monthcalendar(self.year, self.month)
            ]

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['weekdays'] = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        context['weeks'] = self.get_weeks()

        context['formset'] = self.formset
        context['select_form'] = MonthSelectForm(month=self.month, year=self.year)
        context['month'], context['year'] = self.month, self.year
        return context



class LieuCreateView(generic.edit.CreateView):
    """ Vue de création d'un lieu """

    model = Lieu
    template_name = "maraudes/lieu_create.html"
    fields = "__all__"
    success_url = "/maraudes/"

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
