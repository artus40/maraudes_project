from .mixins import *

def _insert_bases(cls, bases):
    old_bases = cls.__bases__
    new_bases = tuple(bases) + old_bases
    cls.__bases__ = new_bases

def webpage(**options):
    """ Class decorators that insert needed bases according to options :
        -- ajax : view will return content_template for Ajax requests
        -- permissions : list of permissions needed to access view
    """
    ajax = options.pop('ajax', False)
    permissions = options.pop('permissions', [])
    app_menu = options.pop('app_menu', [])
    app_name = options.pop('app_name', None)

    new_bases = []
    if ajax:
        new_bases.append(WebsiteAjaxTemplateMixin)
    else:
        new_bases.append(WebsiteTemplateMixin)
    if permissions:
        new_bases.append(PermissionRequiredMixin)

    def class_decorator(cls):
        _insert_bases(cls, new_bases)
        if permissions:
            cls.permissions = permissions
        cls.app_menu = app_menu.copy() #avoid conflict between Views
        cls.app_name = app_name
        return cls

    return class_decorator
