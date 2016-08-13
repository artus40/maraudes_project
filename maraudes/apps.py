from django.apps import AppConfig


class Config(AppConfig):
    name = 'maraudes'

    index_url = "/maraudes/"
    menu_icon = "road"
    def get_index_url(self):
        return "/maraudes/"
