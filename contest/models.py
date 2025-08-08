from django.db import models
from django.conf import settings
from .validators import validate_file_size
# Create your models here.





class Quiz(models.Model):

    SUBJECT_CHOICE = [
        ('MATH','mathematics'),
        ('PHYSICS','physics')
    ]

    title = models.CharField(max_length=255)
    subject = models.CharField(max_length=10, choices=SUBJECT_CHOICE)
    start_time = models.DateTimeField()
    duration_minutes = models.IntegerField(default=20)
    is_rated = models.BooleanField(default=True)
    is_visible = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.title} ({self.subject})"
    



    

    


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
    order = models.PositiveIntegerField()
    is_visible = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    chapter = models.ForeignKey(Chapter, on_delete=models.SET_NULL,null=True,blank=True, related_name='question')
    correct_answer = models.JSONField(default='0')
    contest = models.ForeignKey(Quiz,
                                related_name='questions',
                                on_delete=models.SET_NULL,
                                null=True,
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
        return f"Image for {self.question.title}"


class Submission(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    contest = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)

    selected_options = models.ManyToManyField(QuestionOption,blank=True)
    submitted_value = models.CharField(max_length=155,blank=True,null=True)
    time_taken = models.FloatField()

    class Meta:
        unique_together = ('user','contest','question')


    def __str__(self):
        return f"{self.user} - {self.question} - {self.is_correct}"




    
