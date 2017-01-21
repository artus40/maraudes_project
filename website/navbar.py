""" Draft for navbar application menu """

# We could import a Menu class
# This class could auto-register its children in navbar ?
from django.urls import reverse

registered = []

class Link:
    def __init__(self, text, target="#", icon=None):
        self.text = text
        self.target = target
        self.icon = icon
    
    @property
    def href(self):
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
    def __new__(metacls, name, bases, dct):
        cls = type.__new__(metacls, name, bases, dct)
        if name != "ApplicationMenu":
            print('registering menu', cls)
            registered.append(cls)       
        return cls


class ApplicationMenu(metaclass=MenuRegistry):

    def __init__(self, view):
        try:
            header, target, icon = self.header
        except ValueError:
            header = self.header
            target = "#"
            icon = None
        self.header = Link(header, target, icon)
        self.is_active = False
        self.view = view

    def get_links(self):
        """ Shall be implemented in children. """
        return []

    def get_dropdowns(self, view):
        """ Shall be implemented in children. """
        return []

    @property
    def links(self):
        return [Link(text, target, icon) for text, target, icon in self.get_links()]

    @property
    def dropdowns(self):
        print('getting dropdowns', self, self.view)
        return self.get_dropdowns(self.view)


