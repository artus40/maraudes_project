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
    try: ajax = options.pop('ajax')
    except KeyError: ajax = False
    try: permissions = options.pop('permissions')
    except KeyError: permissions = []
    try: app_menu = options.pop('app_menu')
    except KeyError: app_menu = []
    try: app_name = options.pop('app_name')
    except KeyError: app_name = None

    new_bases = []
    if ajax:
        new_bases.append(WebsiteAjaxTemplateMixin)
    else:
        new_bases.append(WebsiteTemplateMixin)
    if permissions:
        new_bases.append(PermissionRequiredMixin)

    def update_class(cls):
        _insert_bases(cls, new_bases)
        if permissions:
            cls.permissions = permissions
        cls.app_menu = app_menu
        cls.app_name = app_name
        return cls

    return update_class
