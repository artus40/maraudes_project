from django.apps import AppConfig


class Config(AppConfig):
    name = 'maraudes'

    index_url = "/maraudes/"

    def get_index_url(self):
        return "/maraudes/"
