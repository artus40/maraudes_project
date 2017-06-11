
class AjaxTemplateMixin:
    """ Mixin that returns content_template instead of base_template when
        request is Ajax.
    """
    is_ajax = False

    def dispatch(self, request, *args, **kwargs):
        if not hasattr(self, 'ajax_template'):
            self.ajax_template = '%s_inner.html' % self.template_name.split(".")[0]
        if request.is_ajax():
            self.is_ajax = True
        return super().dispatch(request, *args, **kwargs)

    def get_template_names(self):
        if self.is_ajax:
            return [self.ajax_template]
        return super().get_template_names()


