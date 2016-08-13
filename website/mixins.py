import datetime
from django.utils import timezone
from django.core.exceptions import ImproperlyConfigured
from django.apps import apps
from django.contrib.auth.decorators import login_required, permission_required
from django.template import Template, Context
from django.views.generic.base import ContextMixin, TemplateResponseMixin

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



class TemplateFieldsMetaclass(type):
    """ Loads Template objects with given string for
        header, header_small, title, ...

        Theses strings shall be found in cls.Template
    """
    def __init__(cls, bases, Dict):
        pass


def user_processor(request, context):
    context['user_group'] = request.user.groups.first()
    return context

class WebsiteTemplateMixin(TemplateResponseMixin):
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
    app_name = None

    class Configuration:
        stylesheets = ['base.css']
        navbar_apps = ['maraudes', 'suivi']
        apps = get_apps(navbar_apps)
        page_blocks = ['header', 'header_small', 'title']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
        if hasattr(self, 'template_name'): #Ensure easy integration with other views
            self.content_template = self.template_name
        return self.content_template

    def get_active_app(self):
        if not self.app_name:
            self.app_name = self.__class__.__module__.split(".")[0]
        return apps.get_app_config(self.app_name)

    @property
    def active_app(self):
        if not hasattr(self, '_active_app'):
            self._active_app = self.get_active_app()
        return self._active_app

    def get_menu(self):
        """ Renvoie la liste des templates utilisés comme menu pour l'application
            active
        """
        return self.app_menu

    def insert_menu(self, template_name):
        """ Insert menu at beginning of self.app_menu """
        if not template_name in self.app_menu:
            self.app_menu.insert(0, template_name)

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
        context['apps'] = self.Configuration.apps
        context['active_app'] = self.active_app
        # User processor
        context = user_processor(self.request, context)
        #Webpage
        context['content_template'] = self.get_content_template()
        context['app_menu'] = self.get_menu()
        return context

class WebsiteAjaxTemplateMixin(WebsiteTemplateMixin):
    """ Mixin that returns content_template instead of base_template when
        request is Ajax.
    """
    is_ajax = False

    def dispatch(self, request, *args, **kwargs):
        if not hasattr(self, 'content_template') or not self.content_template:
            self.content_template = self.get_content_template()
        if request.is_ajax():
            self.is_ajax = True
        return super().dispatch(request, *args, **kwargs)

    def get_template_names(self):
        if self.is_ajax:
            return [self.content_template]
        return super().get_template_names()

class WebsiteProtectedMixin(WebsiteTemplateMixin, PermissionRequiredMixin):
    pass

class WebsiteProtectedWithAjaxMixin(WebsiteAjaxTemplateMixin, PermissionRequiredMixin):
    pass

