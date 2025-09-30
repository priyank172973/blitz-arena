from django.shortcuts import render
# from django.db.models import Prefetch

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny, IsAdminUser,IsAuthenticatedOrReadOnly
from.models import Chapter,Quiz, Question, QuizQuestion, UserQuizResult,Submission
from.filters import ChapterFilter, QuizFilter
from.serializers import (ChapterSerializer, QuizListSerializer,
                        QuizDetailSerializer, QuizUpdateSerializer,
                        QuestionSerializer,QuizQuestionSerializer,StandingSerializer)
from django.conf import settings

from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.response import Response


class ChapterViewSet(ModelViewSet):
    
    queryset = Chapter.objects.all()
    serializer_class = ChapterSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_class = ChapterFilter

    


class QuizViewSet(ModelViewSet):

    queryset = Quiz.objects.all()
    filter_backends = [DjangoFilterBackend]
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]
    filterset_class = QuizFilter

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminUser()]     # admin-only writes
        return [AllowAny()]
    
    def get_serializer_class(self):
        if self.action == "list":
            return QuizListSerializer
        elif self.action == 'retrieve' and self.request.method == "GET":
            return QuizDetailSerializer
        

        return  QuizUpdateSerializer
    
    def get_queryset(self):
        """
        Keep list() light; prefetch only for retrieve() so detail is fast and ordered.
        """
        qs = super().get_queryset()
        if getattr(self, "action", None) == "retrieve":
            return qs.prefetch_related(
                Prefetch(
                    "quiz_question",
                    queryset=QuizQuestion.objects
                        .select_related("question__chapter")
                        .prefetch_related("question__options")  # if related_name is 'options'; otherwise use 'question__questionoption_set'
                        .order_by("order"),
                )
            )
        return qs
    
    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(qs)

        # HTML branch
        if request.accepted_renderer.format == "html":
            items = page if page is not None else qs
            s = self.get_serializer(items, many=True, context={"request": request})
            return Response(
                {"quizzes": s.data, "is_paginated": page is not None},
                template_name="quizzes/list.html",
            )

        # JSON branch
        if page is not None:
            s = self.get_serializer(page, many=True)
            return self.get_paginated_response(s.data)
        s = self.get_serializer(qs, many=True)
        return Response(s.data)

    def retrieve(self, request, *args, **kwargs):
        quiz = self.get_object()  # uses the prefetching from get_queryset()
        if request.accepted_renderer.format == "html":
            s = self.get_serializer(quiz, context={"request": request})
            return Response({"quiz": s.data}, template_name="quizzes/detail.html")
        s = self.get_serializer(quiz)
        return Response(s.data)
    

class QuestionViewSet(ModelViewSet):

    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]

    queryset = Question.objects.all()
    
    
    serializer_class = QuestionSerializer


    def get_permissions(self):
        if self.action in ['list','retrieve']:
            return [AllowAny()]
        
        return [IsAdminUser()]
        
    def get_queryset(self):
        qs = super().get_queryset()

        user = self.request.user
        if user and user.is_staff:
            return qs

        next_quiz = (Quiz.objects.filter(is_visible = False, quiz_question__isnull = False).order_by('-id').first())
        print(next_quiz.id)

        if not next_quiz:
            print('test1')
            return qs


        next_q_ids = list(QuizQuestion.objects.filter(quiz_id = next_quiz.id).values_list('question_id',flat= True))
        print(next_q_ids)

        if not next_q_ids:
            print('test2')
            return qs
        return qs.exclude(id__in = next_q_ids)
    
#---------------------------CPT CODE BLOCK STARTS HERE--------------------------------------#

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # DRF pagination still works for JSON; for HTML we’ll manually pass items
        page = self.paginate_queryset(queryset)
        if request.accepted_renderer.format == 'html':
            items = page if page is not None else queryset
            serializer = self.get_serializer(items, many=True, context={'request': request})
            return Response(
                {'questions': serializer.data, 'is_paginated': page is not None},
                template_name='questions/list.html'
            )

        # default JSON behavior
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # HTML detail view (optional but handy for per-question page)
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.accepted_renderer.format == 'html':
            serializer = self.get_serializer(instance, context={'request': request})
            return Response({'q': serializer.data}, template_name='questions/detail.html')
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
#---------GPT CODE BLOCK ENDS HERE ---------#

class QuizQuestionViewSet(ModelViewSet):

    

    def get_queryset(self):
        qs = super().get_queryset().select_related(
            'quiz', 'question__chapter'
        ).prefetch_related('question__options')  # adjust related names if needed

        quiz_pk = self.kwargs.get('quiz_pk')  # <-- from NestedDefaultRouter(lookup='quiz')
        if quiz_pk:
            qs = qs.filter(quiz_id=quiz_pk)
        return qs

    serializer_class = QuizQuestionSerializer



class QuizStandingViewSet(ModelViewSet):

    serializer_class = StandingSerializer
    permission_classes = [AllowAny]
    http_method_names = ['get']

    def get_queryset(self):

        quiz_id = self.kwargs.get('quiz_pk')

        return (UserQuizResult.objects
            .select_related("user")
            .filter(quiz_id=quiz_id, is_virtual=False)
            .exclude(status=UserQuizResult.Status.DISQUALIFIED)
            .order_by("-score", "penalties", "created_at", "id")


            )
    
    
    def submission_check(self,submission):

            question = submission.question.question
            
            if question.type == 'SCQ':
                correct_option = question.options.filter(is_correct = True).first()

                if correct_option and submission.selected_options.filter(id= correct_option.id).exists():
                    submission.points_rewarded = question.base_points
                else:
                    submission.points_rewarded = 0

            elif question.type == 'MCQ':
                correct_options = set(question.options.filter(is_correct = True).values_list('id', flat=True))
                selected_options = set(submission.selected_options.values_list('id', flat=True))

                correct_count = len(correct_options & selected_options)
                total_correct = len(correct_options) 

                if total_correct > 0:
                    submission.points_rewarded = (correct_count / total_correct) * question.base_points
                else:
                    submission.points_rewarded = 0  # Or handle this case differently if needed
                
            elif question.type == 'INT':

                correct_answer = question.correct_answer
                if int(correct_answer) == int(submission.submitted_value):
                    submission.points_rewarded = question.base_points
                else:
                    submission.points_rewarded = 0 

            submission.save()





    def list(self, request, **kwargs):

        query_set = self.get_queryset()



        quiz_id = self.kwargs.get('quiz_pk')

    

        for result in query_set:

            submissions = Submission.objects.filter(user_id = result.user_id, quiz_id = result.quiz_id)
            result.correct_answers = 0
            result.penalties = 0
            total_points = 0

            for submission in submissions:
                self.submission_check(submission)
                total_points = total_points + submission.points_rewarded
                

                if submission.points_rewarded>0:
                    result.correct_answers = result.correct_answers + 1
                else:
                    result.penalties = result.penalties + 1
            



            result.score = total_points - result.penalties * settings.PENALTY_MULTIPLIER
        
            result.save()

        serializer = self.get_serializer(query_set, many=True)
        return Response(serializer.data)

         
        
                           

       # Still need to think about this

   