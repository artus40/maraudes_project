""" Draft for navbar application menu 


Defines objects that makes 'navbar' usable.

First, there is the ApplicationMenu class, it is used to define
a Menu for a given set of view. This is done dynamically by the 
Webpage decorator (see website.decorators). This is why this
file is nested inside 'website' app.


Usage :

An application is a set of view, categorized under a name, usually the module name.
A view is handily added to an application using the Webpage decorator, which must
first be instanciated. See website.decorators !

By default, an ApplicationMenu subclass is created for each Webpage instance,
stored inside it's 'app_menu' attribute.

For now, these configurations is done in each apps.py files.
For example, in maraudes/apps.py
> maraudes = Webpage('maraudes', ...)
> maraudes.app_menu.add_link(text, target, icon)
# Add a link to the application menu.

Used as a decorator in views.py:
> @maraudes.using()
> class View: (...)

Dropdowns could be created in apps.py, or directly into view class ?
How to best declare dropdown subclasses ??


"""

from django.urls import reverse
# Shall we use reverse_lazy instead ??

registered = []


class Link:
    """ Navbar link

    Constructor takes one required argument :
        - text : text to display for the link

    and two optional arguments :
        - target : str or tuple
        - icon : bootstrap icon name, no validation

    """

    def __init__(self, text, target="#", icon=None):
        self.text = text
        self.target = target
        self.icon = icon
    
    @property
    def href(self):
        """ Lazy creation of html 'href' value, using 'target' instance attribute """
        if not hasattr(self, '_href'):
            if self.target == "#": #Create void link
                self._href = "#"
            else:
                try:
                    target, kwargs = self.target
                except ValueError:
                    target = self.target
                    kwargs = {}
                assert type(target) == str
                assert type(kwargs) == dict
                self._href = reverse(target, **kwargs)
                # TODO: Add get parameters
                # get_params = kwargs.pop('get')
        return self._href



class DropDown:
 
    header = None

    def get_links(self):
        raise NotImplemented
    
    @property
    def links(self):
        return [Link(text, target, icon) for text, target, icon in self.get_links()]



class MenuRegistry(type):
    """ Metaclass that registers subclass into module level variable 'registered' """
    def __new__(metacls, name, bases, attrs):
        cls = type.__new__(metacls, name, bases, attrs)
        if name != "ApplicationMenu":
            print('registering menu', cls)
            registered.append(cls)
            # Create Link instance for header attributes 
            try:
                header, target, icon = cls.header
            except ValueError:
                header = cls.header
                target = "#"
                icon = None
            cls.header = Link(header, target, icon)
            cls._links = []
            cls._dropdowns = []
        return cls



class ApplicationMenu(metaclass=MenuRegistry):
    name = None
    header = None
    _links = None
    _dropdowns = None

    def __init__(self, view, user):
        self.view = view
        self.user = user
        self.is_active = self.name == self.view.app_name

    @classmethod
    def add_link(cls, link, admin=False):
        if not isinstance(link, Link):
            link = Link(*link)
        link.admin_link = admin
        cls._links.append(link)

    @property
    def links(self):
        if not self.user.is_superuser:
            return filter(lambda l: l.admin_link == False, self._links)
        return self._links

    @property
    def dropdowns(self):
        # add Dropdown instances stored in view ??
        return self._dropdowns


