""" Draft for navbar application menu """

# We could import a Menu class
# This class could auto-register its children in navbar ?
from django.urls import reverse

registered = []

class Link:
    def __init__(self, text, target=None, icon=None):
        self.text = text
        if not target:
            raise TypeError
        if target == "#": #Create void link
            self.href="#"
        else:
            try:
                target, kwargs = target
            except ValueError:
                target = target
                kwargs = {}
            assert type(target) == str
            assert type(kwargs) == dict
            self.href = reverse(target, **kwargs)
        self.icon = icon

class DropDown:
 
    header = None

    def get_links(self):
        raise NotImplemented
    
    @property
    def links(self):
        return [Link(text, target, icon) for text, target, icon in self.get_links()]

class MenuRegistry(type):

    def __new__(metacls, name, bases, dct):
        print('call MenuRegistry.__new__', name, bases, dct)

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


