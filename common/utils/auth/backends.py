from django.contrib.auth.backends import ModelBackend as DJANGOModelBackend


class ModelBackend(DJANGOModelBackend):
    def get_user(self, user_id):
        # user_models = [Administrator, Instructor, ClientStudent]
        # user = None
        # for user_model in user_models:
        #     try:
        #         user = user_model.objects.get(phone=phone)
        #     except ObjectDoesNotExist:
        #         continue
        # try:
        #     user = UserModel._default_manager.get(pk=user_id)
        # except UserModel.DoesNotExist:
        #     return None
        # return user if self.user_can_authenticate(user) else None
        pass
