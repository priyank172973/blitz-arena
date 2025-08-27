from django_filters.rest_framework import FilterSet,CharFilter, BooleanFilter

from. models import Chapter, Quiz



class ChapterFilter(FilterSet):
    subject = CharFilter(field_name='subject', lookup_expr='iexact')

    class Meta:
        model = Chapter
        fields = ['subject']


class QuizFilter(FilterSet):

    subject = CharFilter(field_name='subject', lookup_expr='iexact')
    rating_status = BooleanFilter(field_name = 'is_rated')

    class Meta:
        model = Quiz
        fields = ['subject','rating_status']

    
    

 