import datetime
from django.utils import timezone
from django.core.exceptions import ImproperlyConfigured
from django.apps import apps
from django.contrib.auth.decorators import user_passes_test
from django.template import Template, Context
from django.views.generic.base import ContextMixin, TemplateResponseMixin



## Mixins ##

def special_user_required(authorized_users):

    valid_cls = tuple(authorized_users)

    def check_special_user(user):
        print('check user is instance of', valid_cls)
        if isinstance(user, valid_cls):
            return True
        else:
            return False

    return user_passes_test(check_special_user)


class SpecialUserRequiredMixin(object):
    app_users = []

    @classmethod
    def as_view(cls, **initkwargs):
        view = super().as_view(**initkwargs)
        return special_user_required(cls.app_users)(view)



class TemplateFieldsMetaclass(type):
    """ Loads Template objects with given string for
        header, header_small, title, ...

        Theses strings shall be found in cls.Template
    """
    def __init__(cls, bases, Dict):
        pass


def user_processor(request, context):
    context['user_group'] = request.user.__class__.__qualname__
    return context


class NavbarMixin(object):

    registered_apps = ['maraudes', 'suivi']
    app_name = None



    def get_apps_config(self):
        """ Load additionnal config data on each app registered in navbar
            Add :
            - menu_icon : glyphicon in sidebar
            - disabled : show/hide in sidebar
        """
        ## Utils ##
        APP_ICONS = {
            'maraudes': 'road',
            'suivi': 'eye-open',
        }
        app_names = self.registered_apps
        self._apps = []
        for name in app_names:
            app_config = apps.get_app_config(name)
            app_config.menu_icon = APP_ICONS[name]
            #TODO: Seems unsafe (only need module perm)
            app_config.disabled = not self.request.user.has_module_perms(name)
            self._apps.append(app_config)
        return self._apps

    @property
    def apps(self):
        if not hasattr(self, '_apps'):
            self._apps = self.get_apps_config()
        return self._apps

    def get_active_app(self):
        if not self.app_name:
            self.app_name = self.__class__.__module__.split(".")[0]
        # If app is website, there is no "active" application
        if self.app_name == "website":
            return None

        active_app = apps.get_app_config(self.app_name)
        if not active_app in self.apps: #TODO: how do we deal with this ?
            raise ValueError("%s must be registered in Configuration.navbar_apps" % active_app)
        return active_app

    @property
    def active_app(self):
        if not hasattr(self, '_active_app'):
            self._active_app = self.get_active_app()
        return self._active_app

    @property
    def menu(self):
        """ Renvoie la liste des templates utilisés comme menu pour l'application
            active
        """
        if not self.request.user.is_superuser:
            return self._user_menu
        return self._user_menu + self._admin_menu



class WebsiteTemplateMixin(NavbarMixin, TemplateResponseMixin):
    """ Mixin for easy integration of 'website' templates

        Each child can specify:
        - title : title of the page
        - header : header of the page
        - header_small : sub-header of the page

        If 'content_template' is not defined, value will fallback to template_name
        in child view.
    """
    base_template = "base_site.html"
    content_template = None

    _user_menu = []
    _admin_menu = []
    _groups = []


    class Configuration:
        stylesheets = ['base.css']
        page_blocks = ['header', 'header_small', 'title']


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self._page_blocks = []
        if not hasattr(self, "PageInfo"):
            raise ImproperlyConfigured("You must define a PageInfo on ", self)
        for attr, val in self.PageInfo.__dict__.items():
            if attr[0] is not "_" and type(val) is str:
                setattr(self, attr, Template(val))
                self._page_blocks.append(attr)

    def get_template_names(self):
        """ Ensure same template for all children views. """
        return [self.base_template]

    def get_content_template(self):
        # Ensure easy integration with generic views
        if hasattr(self, 'template_name'):
            self.content_template = self.template_name
        else:
            raise ImproperlyConfigured(self, "has no template defined !")
        return self.content_template


    def _update_context_with_rendered_blocks(self, context):
        """ Render text for existing PageInfo attributes.
            See Configuration.page_blocks for valid attribute names """
        render_context = Context(context)
        for attr in self._page_blocks:
            name = "page_%s" % attr
            context[name] = getattr(self, attr).render(render_context)
        return context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self._update_context_with_rendered_blocks(context)
        #Website processor
        context['stylesheets'] = self.Configuration.stylesheets
        context['apps'] = self.apps
        context['active_app'] = self.active_app
        # User processor
        context = user_processor(self.request, context)
        #Webpage
        context['content_template'] = self.get_content_template()
        context['app_menu'] = self.menu
        return context

class WebsiteAjaxTemplateMixin(WebsiteTemplateMixin):
    """ Mixin that returns content_template instead of base_template when
        request is Ajax.
    """
    is_ajax = False

    def dispatch(self, request, *args, **kwargs):
        if not hasattr(self, 'content_template') or not self.content_template:
            self.content_template = self.get_content_template()
        if not hasattr(self, 'ajax_template'):
            self.ajax_template = '%s_inner.html' % self.content_template.split(".")[0]
        if request.is_ajax():
            self.is_ajax = True
        return super().dispatch(request, *args, **kwargs)

    def get_template_names(self):
        if self.is_ajax:
            return [self.ajax_template]
        return super().get_template_names()


