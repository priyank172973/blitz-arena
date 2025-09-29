from django.contrib import admin
from. import models
from django.utils.html import format_html, urlencode

# Register your models here.



class QuestionOptionInline(admin.TabularInline):
    model = models.QuestionOption
   


class QuestionImageInline(admin.TabularInline):
    model = models.QuestionImage
    readonly_fields = ['thumbnail']

    def thumbnail(self, instance):
        if instance.image.name!='':
            return format_html(f'<img src = "{instance.image.url}"class = "thumbnail"/>')
        return ''




@admin.register(models.Question)
class QuestionAdmin(admin.ModelAdmin):

    list_display = ['title','subject','type','chapter','correct_answer']
    search_fields = ['statement']
    list_filter = ['type','level']

    inlines = [QuestionImageInline,QuestionOptionInline]


@admin.register(models.Quiz)
class QuizAdmin(admin.ModelAdmin):
    
    list_display = ['title','subject','created_at']

    list_filter = ['subject','is_rated']
    search_fields = ['title']



@admin.register(models.QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):

    list_display = ['question_title']

    def question_title(self,quizquestion):
        return quizquestion.question.title

    

@admin.register(models.UserQuizResult)
class UserQuizResultAdmin(admin.ModelAdmin):

    list_display = ['id','user','quiz','rank','score','penalties','status','finalized_at']
    list_filter=['status','quiz']
    search_fields = ('user__username', 'user__email')
    actions = ["finalize_selected_quiz"]



    def finalize_selected_quiz(self, request, queryset):
        pass

    # def quizzes_title(self, question):
    #     return question.quizzes.title