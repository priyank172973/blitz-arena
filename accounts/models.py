from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.



class User(AbstractUser):

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    birth_date = models.DateField(null=True, blank=True)
    rating = models.IntegerField(default=1000)



class UserProfile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name="profile")

    matches = models.PositiveIntegerField(default=0)

    peak_rating = models.IntegerField(default=1000)
    last_rating_change = models.IntegerField(default=0)
    last_active = models.DateTimeField(default=timezone.now)


    def __str__(self):
        return f"Profile({self.user.username})"
    

    @property
    def current_rating(self)->int:
        return self.user.rating



# accounts/models.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance: User, created, **kwargs):
    profile, created_profile = UserProfile.objects.get_or_create(
        user=instance,
        defaults={
            "matches": 0,
            "peak_rating": instance.rating,   # sync initial peak to starting rating
            "last_rating_change": 0,
            "last_active": timezone.now(),
        },
    )

    # If not newly created and rating went up, bump peak
    if not created_profile and instance.rating > profile.peak_rating:
        profile.peak_rating = instance.rating
        profile.save(update_fields=["peak_rating"])