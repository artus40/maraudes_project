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

Added 'LinkManager' to help implement per-view links. How to best do this ?
Specially useful for dropdowns, as Dropdown shall be reactive, thus 
instanciated by DropdownManager when accessed from a Menu instance ??
-> 

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


class LinkManager:
    """ Per-class manager of links """

    def __init__(self):
        self.items = []

    def __get__(self, instance, owner):
        if instance: #Filtering done at each call, not optimized at all !
            if not instance.user.is_superuser:
                return [link for link in self.items if link.admin_link == False]
            else:
                return self.items.copy()
        return self

    def add(self, link):
        self.items.append(link)

    def __repr__(self):
        return '<LinkManager: [' + ', '.join((l.text for l in self.items)) + ']>'



class DropdownManager:
    """ Per-class manager of dropdowns """

    def __init__(self):
        self.items = {}

    def __get__(self, instance, owner):
        if instance:
            key = instance.view.view_class
            return self.items.get(key, self.items.get('default', []))
        return self



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
            cls.links = LinkManager()
            cls.dropdowns = DropdownManager()
        return cls



class ApplicationMenu(metaclass=MenuRegistry):
    name = None
    header = None

    def __init__(self, view, user):
        self.view = view
        self.user = user
        self.is_active = self.name == self.view.app_name

    @classmethod
    def add_link(cls, link, admin=False):
        if not isinstance(link, Link):
            link = Link(*link)
        link.admin_link = admin
        cls.links.add(link)

