import datetime
import calendar
import logging

logger = logging.getLogger(__name__)

from django.utils import timezone
from django.shortcuts import redirect, reverse
from django.views import generic
from django.core.mail import send_mail
from django.forms import modelformset_factory
from django.contrib import messages

from utilisateurs.mixins import MaraudeurMixin

from .models import (   Maraude, Maraudeur,
                        CompteRendu,
                        Rencontre, Lieu,
                        Planning,   )
# Forms
from .forms import (    RencontreForm,
                        ObservationInlineFormSet,
                        MaraudeHiddenDateForm, MonthSelectForm,
                        AppelForm, SignalementForm,
                        SendMailForm   )
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
        return reverse('maraudes:index')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['prochaine_maraude'] = Maraude.objects.get_next_of(self.request.user)
        context['derniers_sujets_rencontres'] = derniers_sujets_rencontres()

        if self.request.user.is_superuser:
            context['missing_cr'] = CompteRendu.objects.get_queryset().filter(
                    heure_fin__isnull=True,
                    date__lt = timezone.localtime(timezone.now()).date()
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
        # Link there so that "Compte-rendu" menu item is not disabled
        context['prochaine_maraude'] = self.object
        return context



class FinalizeView( MaraudeurMixin,
                    generic.detail.SingleObjectMixin,
                    generic.edit.FormView):

    template_name = "maraudes/finalize.html"
    model = Maraude
    form_class = SendMailForm
    success_url = "/maraudes/"

    def get(self, *args, **kwargs):
        print(self.request.GET)
        if bool(self.request.GET.get("no_mail", False)) == True:
            messages.warning(self.request, "Aucun compte-rendu n'a été envoyé !")
            return self.finalize()
        return super().get(*args, **kwargs)

    def get_initial(self):
        maraude = self.get_object()
        objet = "%s - Compte-rendu de maraude" % maraude.date
        sujets_rencontres = set()
        for r in maraude.rencontres.all():
            for s in r.get_sujets():
                sujets_rencontres.add(s)
        message = "Nous avons rencontré : " + ", ".join(map(str, sujets_rencontres)) + ".\n\n"
        return {
            "subject": objet,
            "message": message
        }

    def finalize(self):
        maraude = self.get_object()
        maraude.heure_fin = timezone.localtime(timezone.now()).time()
        maraude.save()
        return redirect(self.get_success_url())

    def form_valid(self, form):
        # Send mail
        maraude = self.get_object()
        recipients = Maraudeur.objects.filter(
                                                is_active=True
                                            ).exclude(
                                                pk__in=(maraude.referent.pk,
                                                        maraude.binome.pk)
                                            )
        result = send_mail(
            form.cleaned_data['subject'],
            form.cleaned_data['message'],
            maraude.referent.email,
            [m.email for m in recipients],
        )

        if result == 1:
            messages.success(self.request, "Le compte-rendu a été transmis à %s" % ", ".join(map(str, recipients)))
        else:
            messages.error(self.request, "Erreur lors de l'envoi du message !")
        return self.finalize()

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        context = super().get_context_data(**kwargs)
        if self.object.est_terminee is True:
            context['form'] = None#Useless form
            return context
        # Link there so that "Compte-rendu" menu item is not disabled
        context['prochaine_maraude'] = self.object
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
        return redirect('maraudes:planning')

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
