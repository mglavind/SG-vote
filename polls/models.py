import datetime

from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import AbstractUser

from django.contrib.admin.models import LogEntry, ADDITION
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Member(AbstractUser):
    # Fields
    username = models.CharField(max_length=30, unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    gang = models.CharField(max_length=100, default="Ingen", blank=True)
    room_number = models.PositiveSmallIntegerField(default="999", blank=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    email = models.EmailField(unique=True)

    class Meta:
        pass

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_absolute_url(self):
        return reverse("polls_member_detail", args=(self.pk,))

    def get_update_url(self):
        return reverse("polls_member_update", args=(self.pk,))

class Question(models.Model):
    question_text = models.CharField(max_length=200, help_text="The actual question")
    pub_date = models.DateTimeField('date published', help_text="The date + time which the question is open for voting")
    is_published = models.BooleanField('is published', help_text="Controls if a question is visible to the members or not")
    closing_date_time = models.DateTimeField('date closing', help_text="The date + time which voting for the question ends ")

    def __str__(self):
        return self.question_text
    
    def is_open(self):
        now = timezone.now()
        if self.is_published :    
            return now <= self.closing_date_time
        else:
            return False

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now
    
    was_published_recently.admin_order_field = 'pub_date'
    was_published_recently.boolean = True
    was_published_recently.short_description = 'Published recently?'


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text


class MemberVote(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)  # Add a choice field


    class Meta:
        unique_together = ('member', 'question')

    def save(self, *args, **kwargs):
        # Check if the member has already voted for this question
        if MemberVote.objects.filter(member=self.member, question=self.question).exists():
            raise ValueError("Member has already voted for this question.")
        super().save(*args, **kwargs)

        # Log the vote action
        question_content_type = ContentType.objects.get_for_model(Question)
        LogEntry.objects.log_action(
            user_id=self.member.id,
            content_type_id=question_content_type.id,
            object_id=self.question.id,
            object_repr="Voted on choice '{}'".format(self.question.question_text),
            action_flag=ADDITION,
            change_message="Voted on choice '{}'".format(self.choice),
        )

    