from rest_framework_nested import routers
from django.urls import path, include
from.views import ChapterViewSet


router = routers.DefaultRouter()

router.register('Chapter',ChapterViewSet)



urlpatterns = router.urls
