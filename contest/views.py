from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny, IsAdminUser,IsAuthenticatedOrReadOnly
from.models import Chapter,Quiz, Question, QuizQuestion
from.filters import ChapterFilter, QuizFilter
from.serializers import (ChapterSerializer, QuizListSerializer,
                        QuizDetailSerializer, QuizUpdateSerializer,
                        QuestionSerializer,QuizQuestionSerializer)

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

