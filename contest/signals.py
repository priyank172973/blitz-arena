from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Submission, UserQuizResult, Question
from django.conf import settings

@receiver(post_save, sender=Submission)
def submission_check(sender, instance, created, **kwargs):

            submission = instance
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
            
            user = submission.user
            quiz = submission.quiz

            result,_= UserQuizResult.objects.get_or_create(user = user, quiz = quiz)

            submissions = Submission.objects.filter(user_id = user.id, quiz_id = quiz.id)

            total_points = 0
            penalties = 0
            correct_answers = 0

            for sub in submissions:
                total_points = total_points + sub.points_rewarded
                if sub.points_rewarded>0:
                    correct_answers += 1
                else:
                    penalties += 1

            result.score = total_points - penalties * settings.PENALTY_MULTIPLIER
            result.correct_answers = correct_answers
            result.penalties = penalties
            result.save()

