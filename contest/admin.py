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

    list_display = ['title','subject','type','chapter','correct_answer','quizzes_title']

    inlines = [QuestionImageInline,QuestionOptionInline]



    def quizzes_title(self, question):
        return question.quizzes.title