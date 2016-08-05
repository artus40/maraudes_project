import datetime
from django.utils import timezone
from django.views.generic.base import ContextMixin, TemplateResponseMixin

from django.apps import apps
from django.contrib.auth.decorators import login_required, permission_required

## Utils ##
def get_apps(app_names):
    _apps = []
    for name in app_names:
        _apps.append(
            apps.get_app_config(name)
        )
    return _apps

## Mixins ##

class PermissionRequiredMixin(object):
    permissions = []
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(PermissionRequiredMixin, cls).as_view(**initkwargs)
        return permission_required(cls.permissions)(view)


class AjaxTemplateMixin(object):
    """ Mixin that enables the use of 'ajax_template_name' custom template
        when request is Ajax.
    """
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(self, 'ajax_template_name'):
            raise NotImplementedError
        if request.is_ajax():
            self.template_name = self.ajax_template_name
        return super(AjaxTemplateMixin, self).dispatch(request, *args, **kwargs)



class TemplateFieldsMetaclass(type):
    """ Loads Template objects with given string for
        header, header_small, title, ...

        Theses strings shall be found in cls.Template
    """
    def __init__(cls, bases, Dict):
        pass



class WebsiteTemplateMixin(TemplateResponseMixin):
    """ Mixin for easy integration of 'website' templates

        Each child can specify:
        - title : title of the page
        - header : header of the page
        - header_small : sub-header of the page

        If 'content_template' is not defined, value will fallback to template_name
        in child view.
    """

    #TODO: class Template:
    title = "Maraudes ALSA"
    header = "Page Header"
    header_small = None
    content_template = None

    class Configuration:
        stylesheets = ['base.css']
        navbar_apps = ['maraudes', 'suivi']

        apps = get_apps(navbar_apps)

    def get_template_names(self):
        """ Ensure same template for all children views. """
        return ["base_site.html"]

    def get_content_template(self):
        if hasattr(self, 'template_name'): #Ensure easy integration with other views
            self.content_template = self.template_name
        return self.content_template

    def get_active_app(self, app_name=None):
        if not app_name:
            app_name = self.__class__.__module__.split(".")[0]
        return apps.get_app_config(app_name)

    def get_panels(self):
        """ Panneaux """
        return None

    def get_prochaine_maraude_for_user(self):
        """ Retourne le prochain objet Maraude auquel
            l'utilisateur participe, ou None """
        maraudeur_cls = apps.get_model('utilisateurs', model_name="Maraudeur")
        maraude_cls = apps.get_model('maraudes', model_name="Maraude")
        try: #TODO: Clean up this ugly thing
            self.maraudeur = maraudeur_cls.objects.get(username=self.request.user.username)
        except:
            self.maraudeur = None

        if self.maraudeur:
            return maraude_cls.objects.get_next_of(self.maraudeur)
        return None

    def get_prochaine_maraude(self):
        return apps.get_model('maraudes', model_name="Maraude").objects.next

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['stylesheets'] = self.Configuration.stylesheets
        context['apps'] = self.Configuration.apps
        context['active_app'] = self.get_active_app()

        context['page_title'] = self.title
        context['page_header'] = self.header
        context['page_header_small'] = self.header_small

        context['content_template'] = self.get_content_template()
        context['panels'] = self.get_panels()

        context['prochaine_maraude_abs'] = self.get_prochaine_maraude()
        context['prochaine_maraude'] = self.get_prochaine_maraude_for_user()
        return context


class WebsiteProtectedMixin(WebsiteTemplateMixin, PermissionRequiredMixin):
    pass

class WebsiteProtectedWithAjaxMixin(WebsiteProtectedMixin, AjaxTemplateMixin):
    pass

## Views : Index ##

from django.shortcuts import redirect

def index_view(request):
    if not request.user.is_authenticated():
        return redirect('login')
    else:
        return redirect('maraudes:index')
