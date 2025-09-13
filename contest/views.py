from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny, IsAdminUser,IsAuthenticatedOrReadOnly
from.models import Chapter,Quiz, Question, QuizQuestion, UserQuizResult,Submission
from.filters import ChapterFilter, QuizFilter
from.serializers import (ChapterSerializer, QuizListSerializer,
                        QuizDetailSerializer, QuizUpdateSerializer,
                        QuestionSerializer,QuizQuestionSerializer,StandingSerializer)
from django.conf import settings

class ChapterViewSet(ModelViewSet):
    
    queryset = Chapter.objects.all()
    serializer_class = ChapterSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_class = ChapterFilter

    



class QuizViewSet(ModelViewSet):

    queryset = Quiz.objects.all()

    filter_backends = [DjangoFilterBackend]
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
    

class QuestionViewSet(ModelViewSet):

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


        print('test3')
        return qs.exclude(id__in = next_q_ids)
    


class QuizQuestionViewSet(ModelViewSet):

     queryset = QuizQuestion.objects.all()

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

   