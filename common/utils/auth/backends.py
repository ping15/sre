from django.contrib.auth.backends import ModelBackend as DJANGOModelBackend
from django.core.exceptions import ObjectDoesNotExist

from apps.platform_management.models import Administrator, Instructor, ClientStudent


class ModelBackend(DJANGOModelBackend):
    def get_user(self, user_id):
        user_models = [Administrator, Instructor, ClientStudent]
        user = None
        for user_model in user_models:
            try:
                user = user_model.objects.get(phone=user_id)
                break
            except ObjectDoesNotExist:
                continue
        return user
