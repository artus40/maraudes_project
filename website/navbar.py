""" Draft for navbar application menu 
"""

from django.urls import reverse

registered = []


class Link:
    """ Navbar link

    Constructor takes one required argument :
        - text : text to display for the link

    and two optional arguments :
        - target : str or tuple (str, dict)
        - icon : bootstrap icon name, no validation

    """

    def __init__(self, text, target="#", icon=None):
        self.text = text
        self._target = target
        self.icon = icon

    @property
    def href(self):
        """ Lazy creation of html 'href' value, using 'target' instance attribute """
        if not hasattr(self, '_href'):
            if self._target == "#": #Create void link
                self._href = "#"
            else:
                try:
                    target, kwargs = self._target
                except ValueError:
                    target = self._target
                    kwargs = {}
                assert type(target) == str
                assert type(kwargs) == dict
                self._href = reverse(target, **kwargs)
        return self._href



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

