from .mixins import (WebsiteTemplateMixin, WebsiteAjaxTemplateMixin,
                    SpecialUserRequiredMixin)
from .navbar import ApplicationMenu



def _insert_bases(cls, bases):
    """ Insert new bases in given view class """
    old_bases = cls.__bases__
    new_bases = tuple(bases) + old_bases
    cls.__bases__ = new_bases



class Webpage:
    """ Webpage configurator. It is used as a decorator.

    The constructor takes one positionnal argument:
        - app_name : name of the application where this view shall be categorized.
    and keyword arguments:
        - defaults : mapping of default options.
        - menu : does it register a menu ? default is True
        - icon : bootstrap name of menu header icon, ignored if 'menu' is False.

    Options are :
        - title: tuple of (header, header_small), header_small is optionnal.
        - restricted: set of group to which access is restricted.
        - ajax: can this view be called as ajax ?

    """

    options = [
            ('title', ('Unset', 'small header')),
            ('restricted', []),
            ('ajax', False)
        ]

    def __init__(self, app_name, icon=None, defaults={}, menu=True):
        self.app_name = app_name

        if menu: # Build ApplicationMenu subclass
            app_menu = type(
                        app_name.title() + "Menu",
                        (ApplicationMenu,),
                        {'name': app_name,
                         'header': (app_name.title(), '%s:index' % app_name, icon),
                        }
                    )
            self.app_menu = app_menu
        else:
            self.app_menu = None

        self._defaults = {}
        self._updated = {} # Store updated options
        # Set all default options
        for opt_name, opt_default in self.options:
            self._set_option(opt_name, defaults.get(opt_name, opt_default))

    def __getattr__(self, attr):
        """ Return the overriden value if any, default overwise """
        return self._updated.get(attr, self._defaults[attr])
    
    def _set_option(self, attr, value):
        """ Set the default value if there is none already, updated overwise """
        if not attr in self._defaults:
            self._defaults[attr] = value
        else:
            if attr in self._updated:
                raise RuntimeError(attr, 'has already been updated !')
            self._updated[attr] = value

    def __call__(self, view_cls):
        """ Setup the view and return it """
        bases_to_add = []
        if self.ajax:       bases_to_add.append(WebsiteAjaxTemplateMixin)
        else:               bases_to_add.append(WebsiteTemplateMixin)
        if self.restricted: bases_to_add.append(SpecialUserRequiredMixin)
        _insert_bases(view_cls, bases_to_add)
        # Setup configuration. ISSUE: defaults values will be overriden !
        view_cls.app_name = self.app_name
        view_cls.header = self.title
        view_cls.app_users = self.restricted
        self._updated = {} # Reset updated attributes to avoid misbehavior
        return view_cls

    def using(self, **kwargs):
        """ Overrides defaults options with the values given """
        for opt_name, _ in self.options:
            if opt_name in kwargs:
                self._set_option(opt_name, kwargs[opt_name])
        return self
