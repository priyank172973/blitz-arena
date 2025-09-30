
from django.db import transaction
from rest_framework import serializers
from .models import Chapter, Quiz, QuizQuestion, Question, QuestionOption, UserQuizResult


class ChapterSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Chapter

        fields = ['title','subject']

class OptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = QuestionOption

        fields = ['id','text']

class QuestionSerializer(serializers.ModelSerializer):

    chapter = ChapterSerializer()
    options = OptionSerializer(many = True)

    class Meta:
        model = Question

        fields = ['title','chapter','statement','options','type']

class QuizQuestionSerializer(serializers.ModelSerializer):

    question = QuestionSerializer()
    class Meta:
        model = QuizQuestion

        fields = ['id','order','question','quiz_id']

class QuizDetailSerializer(serializers.ModelSerializer):

    quiz_question = QuizQuestionSerializer(many = True)

    #questions = QuizQuestionSerializer(many = True, write_only = True,required = False)
    questions_remove = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=False,
    )
    

    class Meta:

        model = Quiz

        fields = ['id', 'title','subject','created_at','is_rated','penalty_per_wrong','duration_minutes','quiz_question','questions_remove']

class QuizListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ['id', 'title', 'subject', 'created_at', 'is_rated', 'penalty_per_wrong']



class QuizQuestionItemSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    order = serializers.IntegerField(min_value = 1)
    base_points = serializers.IntegerField(min_value =0, default = 10)

class QuizUpdateSerializer(serializers.ModelSerializer):


    questions = QuizQuestionItemSerializer(many = True, write_only = True,required = False)
    questions_remove = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=False
    )

    class Meta:
        model = Quiz


        fields = [ "title", "subject", "duration_minutes",
            "is_rated", "is_visible","penalty_per_wrong","questions",'questions_remove']
        
        read_only_fields = ['created_at']
        
    def validate_questions(self, items):
        if items is None:
            return items
        
        if not items:
            return items
        qids = [it["question_id"] for it in items]
        existing = set(Question.objects.filter(id__in = qids).values_list('id', flat=True))
    
        missing = [qid for qid in qids if qid not in existing]
        if missing:
            raise serializers.ValidationError(f"Question ID found :{missing}")
        
        orders = [it['order'] for it in items]
        if len(orders) != len(set(orders)):
            raise serializers.ValidationError("Duplicate 'order' values are not allowed")
        
        return items
    


    def _replace_quiz_questions(self, quiz: Quiz, items):
        QuizQuestion.objects.filter(quiz=quiz).delete()
        if not items:
            return
        QuizQuestion.objects.bulk_create([
            QuizQuestion(
                quiz=quiz,
                question_id=it["question_id"],
                order=it["order"],
                base_points=it.get("base_points", 10),
            )
            for it in items
        ])

    @transaction.atomic
    def create(self, validated_data):
        items = validated_data.pop("questions", [])
        quiz = super().create(validated_data)
        self._replace_quiz_questions(quiz, items)
        return quiz

    @transaction.atomic
    def update(self, instance, validated_data):
        items_replace = validated_data.pop("questions", None)  
        to_remove = validated_data.pop('questions_remove', None)# None => leave as-is
        
        quiz = super().update(instance, validated_data)
        
        if items_replace is not None:
            self._replace_quiz_questions(quiz, items_replace)
            

        # Partial remove (if provided)
        if to_remove:
            QuizQuestion.objects.filter(
                quiz=quiz,
                question_id__in=to_remove
            ).delete()

        return quiz



class StandingSerializer(serializers.ModelSerializer):

    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:

        model = UserQuizResult
        fields = ['user_id','username','score','correct_answers','penalties','rank','status']

