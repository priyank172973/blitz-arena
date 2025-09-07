from rest_framework_nested import routers
from django.urls import path, include
from.views import ChapterViewSet, QuizViewSet, QuestionViewSet,QuizQuestionViewSet, QuizStandingViewSet


router = routers.DefaultRouter()

router.register('Chapters',ChapterViewSet)

router.register('Quizzes', QuizViewSet)

router.register('Questions', QuestionViewSet)

#router.register('QuizQuestion',QuizQuestionViewSet)


quiz_router = routers.NestedDefaultRouter(
    router, 'Quizzes', lookup='quiz')

quiz_router.register('results',QuizStandingViewSet,basename='quiz-result')




urlpatterns = router.urls + quiz_router.urls
