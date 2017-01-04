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



class ApplicationMenu:

    def __init__(self):
        try:
            header, target, icon = self.header
        except ValueError:
            header = self.header
            target = "#"
            icon = None
        self.header = Link(header, target, icon)
        self.is_active = False
        
        # Register the instance into module
        registered.append(self)

    def get_links(self):
        """ Shall be implemented in children. """
        return []

    def get_dropdowns(self):
        """ Shall be implemented in children. """
        return []

    @property
    def links(self):
        return self.get_links()

    @property
    def dropdowns(self):
        return self.get_dropdowns()


