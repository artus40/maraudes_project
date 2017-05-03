import logging
from django.contrib.auth.backends import ModelBackend
from .models import Maraudeur

logger = logging.getLogger(__name__)

AUTHORIZED_MODELS = (Maraudeur, )

class CustomUserAuthentication(ModelBackend):
    """ Custom ModelBackend that can only return an authorized custom models """

    def get_user(self, user_id):
        logger.info("CALL: CustomUserAuthentication.get_user with id: ", user_id)
        user = super().get_user(user_id)
        if not user:
            return None

        for model in AUTHORIZED_MODELS:
            try:
                return model.objects.get(user_ptr=user)
            except:
                continue

        logger.warning("WARNING: Could not find any AUTHORIZED_MODEL for %s !" % user)
        return user

    def has_perm(self, *args, **kwargs):
        print('call has_perm', args, kwargs)
        return super().has_perm(*args, **kwargs)
