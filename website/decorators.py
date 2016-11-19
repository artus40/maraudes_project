from .mixins import *

def _insert_bases(cls, bases):
    old_bases = cls.__bases__
    new_bases = tuple(bases) + old_bases
    cls.__bases__ = new_bases

def app_config(**options):
    """ Insert per-application configuration options :
        -- name : name of the app to register under in navbar
        -- groups : user groups needed to access this application
        -- menu : user menu templates to be used
        -- admin_menu : admin menu templates, only appear for superuser
        -- ajax : view will return content_template for Ajax requests
    """
    name = options.pop('name', None)
    groups = options.pop('groups', []) #Transition from app_users
    menu = options.pop('menu', [])
    admin_menu = options.pop('admin_menu', [])
    ajax = options.pop('ajax', False)

    new_bases = []
    if ajax:
        new_bases.append(WebsiteAjaxTemplateMixin)
    else:
        new_bases.append(WebsiteTemplateMixin)

    if groups: #TODO: use group instaed of user class
        new_bases.append(SpecialUserRequiredMixin)

    def class_decorator(cls):
        _insert_bases(cls, new_bases)
        cls._user_menu = menu
        cls._admin_menu = admin_menu
        cls.app_name = name
        cls.app_users = groups.copy()
        return cls

    return class_decorator
