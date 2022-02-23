from django.urls               import path, include
from rest_framework            import routers

from account.views.user_views  import UserViewSet
from account.views             import social_login_view

router = routers.SimpleRouter(trailing_slash=True)
router.register('', UserViewSet, basename='user-viewset')


urlpatterns = [
    path('', include(router.urls)),
    path('kakao/auth/', social_login_view.kakao_authorization_code, name='kakao_auth_code'),
    path('kakao/auth-callback/', social_login_view.kakao_authorization_code_callback, name='kakao_auth_code_callback'),
    path('kakao/profile/', social_login_view.kakao_profile, name='kakao_profile'),
]

urlpatterns += router.urls
