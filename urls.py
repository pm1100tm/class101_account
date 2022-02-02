from django.urls    import path, include
from rest_framework import routers

from account.views  import UserViewSet


router = routers.SimpleRouter(trailing_slash=True)
router.register('', UserViewSet, basename='user-viewset')

urlpatterns = router.urls

# urlpatterns = [
#     path('', include(router.urls)),
# ]
