from rest_framework_nested import routers
from django.urls import path, include
from.views import ChapterViewSet, QuizViewSet, QuestionViewSet,QuizQuestionViewSet


router = routers.DefaultRouter()

router.register('Chapter',ChapterViewSet)

router.register('Quiz', QuizViewSet)

router.register('Question', QuestionViewSet)

router.register('QuizQuestion',QuizQuestionViewSet)


urlpatterns = router.urls
