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

# Doing the same as class

class Webpage:
    """ Webpage configurator.
    
    Used as a decorator :
    
    Set default for any app constructing an instance.
    maraudes = Webpage(title=('Maraudes', 'app'), menu={'links': [], 'dropdowns': []})

    Then use as a decorator on app views. You can change options by calling
    appropriated methods :
        - header: title=('Big header',  'small one') ; Can use template syntax with view context variables
        - menu : links=[], dropdowns=[], replace=False


    """

    def __init__(self, **options):
        try:
            self.app_name = options.get('name')
        except KeyError:
            raise TypeError('Webpage configurator must be given an application "name"')
        self._defaults = {} # Store default options
        self._updated = {} # Store updated options
        # Set all attributes a first time, causing all defaults to be filled
        self.title(*options.get('title', ('None', 'none')))
        self.restricted(options.get('groups', []), replace=True)
        self.is_ajax(options.get('ajax', False))
        # self.menu(...)
        # Further calls to these methods will set _updated instead of defaults.

    def __getattr__(self, attr):
        """ Return the overriden value if any, default overwise """
        return self._updated.get(attr, self._defaults[attr])
    
    def __setattr__(self, attr, value):
        """ Set the default value if there is none already, updated overwise """
        if not attr in self._defaults:
            self._defaults[attr] = value
        else:
            if attr in self._udpated:
                raise ValueError(attr, 'has already been updated !')
            self._updated[attr] = value

    def __call__(self, view_cls):
        """ Setup the view and return it """
        bases_to_add = []
        if self.is_ajax:    bases_to_add.append(WebsiteAjaxTemplateMixin)
        else:               bases_to_add.append(WebsiteTemplateMixin)
        if self.restricted: bases_to_add.append(SpecialUserRequiredMixin)
        _insert_bases(cls, bases_to_add)
        # Setup configuration. ISSUE: defaults values will be overriden !
        cls.app_name = self.app_name
        #...
        
        self._updated = {} # Reset updated attributes to avoid misbehavior
        return cls

    def title(self, header='', header_small=''):
        """ Sets the title and header of this view. Takes up to two arguments:
            1. header
            2. header_small

            Title will be set to  header - header_small'
        """
        if not args: 
            return self
        
        self.header = header
        self.header_small = header_small
        # self.title = ' - '.join()
        return self

    def menu(self, links=[], dropdowns=[], replace_links=False, replace_dropdowns=False):
        if links:
            if not replace_links:
                self.links += links
            else:
                self.links = links
        if dropdowns:
            if not replace_dropdowns:
                self.dropdowns += dropdowns
            else:
                self.dropdowns = dropdowns
        return self

    def is_ajax(self, value):
        self.is_ajax = bool(value)
        return self

    def restricted(self, users, replace=False):
        if not replace:
            self.users += users
        else:
            self.users = users
        return self

