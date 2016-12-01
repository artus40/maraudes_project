from django.views import generic


from website import decorators as website
stats = website.app_config(
                    name="statistiques",
                    groups=[],
                    menu=[],
                    admin_menu=[],
                    ajax=False,
                )

@stats
class IndexPage(generic.TemplateView):
    class PageInfo:
        title = "Statistiques"
        header = "Statistiques"
        header_small = "index"
    # TemplateView
    template_name = "statistiques/index.html"
