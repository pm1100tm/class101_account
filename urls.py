from django.urls    import path, include
from rest_framework import routers

from account.views  import UserViewSet, signup_kakao, signup_kakao_callback, signup_kakao_get_profile


router = routers.SimpleRouter(trailing_slash=True)
router.register('', UserViewSet, basename='user-viewset')


urlpatterns = [
    # path('', include(router.urls)),
    path('sign-up/kakao/', signup_kakao, name='sign_up_kakao'),
    path('sign-up/kakao-callback/', signup_kakao_callback, name='sign_up_kakao_callback'),
    path('sign-up/kakao-profile/', signup_kakao_get_profile, name='sign_up_kakao_profile'),
]

urlpatterns += router.urls
