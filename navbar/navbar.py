""" Draft for navbar application menu """

# We could import a Menu class
# This class could auto-register its children in navbar ?


##BEGIN: navbar/menu.py

class Link:
    
    text = ""
    href = ""
    icon = None

    def __init__(self, text, target, args=(), kwargs={}, icon=None):
        from django.urls import reverse

        self.text = text
        self.icon = None
        self.href = reverse(target, args=args, kwargs=kwargs)

    def render(self):
        html = "<li class='app-menu'>\n\
\t<a href='%(href)s'>\n\
\t\t%(text)s\n\
\t\t<span class='pull-right'><span class='glyphicon glyphicon-$(icon)s'></span></span>\n\
\t</a>\n\
</li>" % self.__dict__
        return(html)

class Dropdown:
    
    header = ""
    links = None
    
    def __init__(self, header, links):
        self.header = header
        self.links = tuple(Link(*args) for args in links)

    def render(self):
        html = "<li class='dropdown app-menu'>\n\
\t<a class='dropdown-toggle' data-toggle='dropdown' href='#'>%(header)s <b class='caret'></b></a>\n\
\t<ul class='dropdown-menu'>\n" % self.__dict__
        for link in self.links:
            html += self.render_link(link)
        html += "\n\t</ul>\n</li>"
        return html

    def render_link(self, link):
        """ Overrides Link.render method, set on link by Dropdown """
        html = "\t<li>\n\
\t\t<a href='%(href)s'>\n\
\t\t\t<span class='glyphicon glyphicon-%(icon)s'></span>\n\
\t\t\t%(text)s\n\
\t\t</a>\n\
\t</li>" % link.__dict__
        return html


class Menu:
    """ Base class for navbar menus.

    It defines a set of (name, target) link that are styled into bootstrap navbar.
    It shall handle sections and subsections.

    Index is the main page of the module, used as header for the menu.
    If application has no index (like 'utilisateurs'), what to do ?

    """
    pass

##END: navbar/menu.py
"""
maraudes_menu = (
    Link('Maraudes', 'maraudes:index'),
    Link('Liste des maraudes', 'maraudes:liste'),
    Dropdown('Dernières maraudes', []),
    Dropdown('Admin', [('Planning', 'maraudes:planning'), ('Gérer les maraudes', 'admin:maraudes')]),
)
"""
# Each view would be able to define a menu that is added, or override default one

