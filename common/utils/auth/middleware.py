from django.contrib.auth.middleware import (
    AuthenticationMiddleware as DRFAuthenticationMiddleware,
)


# class AuthenticationMiddleware(DRFAuthenticationMiddleware):
#     def process_request(self, request):
#         assert hasattr(request, 'session'), (
#             "The Django authentication middleware requires session middleware "
#             "to be installed. Edit your MIDDLEWARE setting to insert "
#             "'django.contrib.sessions.middleware.SessionMiddleware' before "
#             "'django.contrib.auth.middleware.AuthenticationMiddleware'."
#         )
#         request.user = SimpleLazyObject(lambda: get_user(request))
