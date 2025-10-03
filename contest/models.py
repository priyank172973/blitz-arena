from django.db import models
from django.conf import settings
from .validators import validate_file_size
# Create your models here.



User = settings.AUTH_USER_MODEL

class Quiz(models.Model):

    SUBJECT_CHOICE = [
        ('MATH','mathematics'),
        ('PHYSICS','physics')
    ]

    title = models.CharField(max_length=255)
    subject = models.CharField(max_length=10, choices=SUBJECT_CHOICE)
    created_at = models.DateTimeField()
    duration_minutes = models.IntegerField(default=20)
    is_rated = models.BooleanField(default=True)
    is_visible = models.BooleanField(default=False)
    penalty_per_wrong = models.IntegerField(default=0)



    class Meta:
        verbose_name_plural = "Quizzes"


    def __str__(self) -> str:
        return f"{self.title} ({self.subject})"
    
class Chapter(models.Model):

    title = models.CharField(max_length=155)

    subject = models.CharField(max_length=20, choices=[
        ('Physics', 'Physics'),
        ('Maths', 'Maths'),
    ])




    def __str__(self):
        return self.title

class Question(models.Model):

    SUBJECT_CHOICE = [
        ('MATH','mathematics'),
        ('PHYSICS','physics')
    ]

    LEVEL_CHOICES = [
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard')
    ]

    TYPE_SINGLE = 'SCQ'  
    TYPE_MULTI = 'MCQ'    
    TYPE_INTEGER = 'INT' 

    TYPE_CHOICES = [
        (TYPE_SINGLE, 'Single Correct'),
        (TYPE_MULTI, 'Multiple Correct'),
        (TYPE_INTEGER, 'Integer Type'),
    ]

    title = models.CharField(max_length=155)
    level = models.CharField(max_length=10,choices=LEVEL_CHOICES)
    subject = models.CharField(max_length=20, choices=SUBJECT_CHOICE)
    statement = models.TextField()
    type = models.CharField(max_length=10,choices=TYPE_CHOICES)
    is_visible = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    chapter = models.ForeignKey(Chapter, on_delete=models.SET_NULL,null=True,blank=True, related_name='question') #need to update many-to
    correct_answer = models.CharField(max_length=50,null=True)
    quizzes = models.ManyToManyField('Quiz',
                                related_name='questions',
                                through='QuizQuestion',
                                blank=True
                                )
    
    

    def __str__(self):
        return f"{self.title} ({self.get_type_display()})"
    
class QuestionImage(models.Model):

    question = models.ForeignKey(Question, on_delete= models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='contest/image',validators=[validate_file_size],blank=True,null=True)
    captions = models.CharField(max_length=200,blank=True)

class QuestionOption(models.Model):

    question = models.ForeignKey(Question, on_delete= models.CASCADE,related_name='options')
    text = models.CharField(max_length=300, blank=True)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"Options for Q{self.question.id}:{self.text}"
    
class QuizQuestion(models.Model):

    quiz = models.ForeignKey('Quiz', on_delete=models.CASCADE,related_name='quiz_question')
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    
    order = models.PositiveIntegerField(default=1)
    base_points = models.PositiveIntegerField(default=100)

    class Meta:
        unique_together = ('quiz','question')

class Submission(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)

    selected_options = models.ManyToManyField(QuestionOption,blank=True)
    submitted_value = models.CharField(max_length=155,blank=True,null=True)
    time_taken = models.FloatField()

    points_rewarded = models.DecimalField(max_digits=7, decimal_places=2, default=0)

    class Meta:
        unique_together = ('user','quiz','question')


    def __str__(self):
        return f"{self.user} - {self.question} - {self.is_correct}"

class UserQuizResult(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        FINALIZED = "FINALIZED", "Finalized"
        DISQUALIFIED = "DQ", "Disqualified"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="result")
    quiz = models.ForeignKey("Quiz", on_delete=models.CASCADE, related_name="results")

    rank = models.PositiveIntegerField(null=True, blank=True)
    score = models.FloatField(default=0)
    correct_answers = models.PositiveIntegerField(default=0)
    penalties = models.IntegerField(default=0)

    old_rating = models.IntegerField(null=True, blank=True)
    new_rating = models.IntegerField(null=True, blank=True)
    rating_change = models.IntegerField(null=True, blank=True)

    is_virtual = models.BooleanField(default=False)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)

    created_at = models.DateTimeField(auto_now_add=True)
    finalized_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "quiz"],
                condition=models.Q(is_virtual=False),
                name="uniq_live_result_per_user_quiz",
            )
        ]
       

    # def __str__(self):
    #     return f"{self.user} @ {self.quiz} rank={self.rank} Δ={self.rating_change or 0:+}"

    
