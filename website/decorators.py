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
        return cls

    return update_class
