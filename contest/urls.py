from rest_framework_nested import routers
from django.urls import path, include
from.views import ChapterViewSet, QuizViewSet, QuestionViewSet,QuizQuestionViewSet, QuizStandingViewSet


router = routers.DefaultRouter()

router.register('Chapters',ChapterViewSet)

router.register('Quizzes', QuizViewSet)

router.register('Questions', QuestionViewSet)

#router.register('QuizQuestion',QuizQuestionViewSet)


# urls.py
quiz_router = routers.NestedDefaultRouter(router, r'Quizzes', lookup='quiz')
quiz_router.register(r'questions', QuizQuestionViewSet, basename='quiz-questions')




# quiz_router = routers.NestedDefaultRouter(router, r'quizzes', lookup='quiz')
# quiz_router.register(r'questions', QuizViewSet, basename='quiz-questions')   # <-- THIS

# quiz_router.register(r'results', QuizStandingViewSet, basename='quiz-result')





urlpatterns = router.urls + quiz_router.urls
