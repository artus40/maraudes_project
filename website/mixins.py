from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin

from django.template import Template, Context, loader
from django.views.generic.base import TemplateResponseMixin

## Mixins ##



class SpecialUserRequiredMixin(object):
    """ Requires that the User is an instance of some class """
    app_users = []

    @classmethod
    def as_view(cls, **initkwargs):
        view = super().as_view(**initkwargs)
        return cls.special_user_required(cls.app_users)(view)

    @staticmethod
    def special_user_required(authorized_users):
        valid_cls = tuple(authorized_users)
        if not valid_cls: # No restriction usually means misconfiguration !
                raise ImproperlyConfigured(
'A view was configured as "restricted" with no restricting parameters !')

        def check_special_user(user):
            if isinstance(user, valid_cls):
                return True
            else:
                return False
        return user_passes_test(check_special_user)


def user_processor(request, context):
    context['user_group'] = request.user.__class__.__qualname__
    return context

def header_processor(header, context):
    context['page_header'] = Template(header[0]).render(context)
    context['page_header_small'] = Template(header[1]).render(context) if len(header) == 2 else ''
    context['page_title'] = " - ".join((context['page_header'], context['page_header_small']))
    return context



class WebsiteTemplateMixin(TemplateResponseMixin):
    """ Mixin for easy integration of 'website' templates

        If 'content_template' is not defined, value will fallback to template_name
        in child view.
    """
    base_template = "base_site.html"
    content_template = None
    app_name = None

    class Configuration:
        stylesheets = ['css/base.css']


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None

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

    def get_extra_templates(self, context):
        """ Loads extra menu and toolbox templates, if any, into context """
        if self.app_name:
            context['menu_template'] = self.app_name + "/menu.html"
        return context

    def get_context_data(self, **kwargs):
        context = Context(super().get_context_data(**kwargs))
        #Website processor
        context['stylesheets'] = self.Configuration.stylesheets
        context['active_app'] = self.app_name # Set by Webpage decorator
        # User processor
        context = header_processor(self.header, context)
        context = user_processor(self.request, context)
        #Webpage
        context['content_template'] = self.get_content_template()
        context = self.get_extra_templates(context)
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


