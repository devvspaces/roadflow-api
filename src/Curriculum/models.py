from functools import reduce

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from sqlalchemy import all_

from Curriculum.managers import SyllabiProgressManager
from Quiz.models import Quiz
from utils.base.general import get_unique_slug


class Curriculum(models.Model):
    """Curriculum Model"""

    DIFFICULTY = (
        ('B', 'Beginner'),
        ('I', 'Intermediate'),
        ('A', 'Advanced'),
    )

    name = models.CharField(max_length=255, null=False,
                            blank=False, unique=True)
    slug = models.SlugField(max_length=255, null=True,
                            blank=True, unique=True)
    description = models.TextField(null=False, blank=False)
    objective = models.TextField(null=False, blank=False)
    prerequisites = models.TextField(null=False, blank=False)
    enrolled = models.IntegerField(default=0)
    difficulty = models.CharField(
        choices=DIFFICULTY, max_length=1, null=False, blank=False)
    resources = models.ManyToManyField('Resource.Resource', blank=True)
    rating = models.FloatField(default=0.0)
    ratings = models.IntegerField(default=0)

    def get_syllabus(self) -> models.QuerySet['CurriculumSyllabi']:
        return self.curriculumsyllabi_set.all()

    @property
    def syllabus(self) -> models.QuerySet['CurriculumSyllabi']:
        return self.get_syllabus()

    def get_next_order(self):
        last = self.get_syllabus().last()
        if last:
            return last.order + 1
        return 1

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = get_unique_slug(self.name, self)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class CurriculumSyllabi(models.Model):
    """Curriculum Syllabi Model"""

    curriculum = models.ForeignKey(
        Curriculum, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)
    title = models.CharField(max_length=255, null=False, blank=False)
    slug = models.SlugField(max_length=255, null=True,
                            blank=True, unique=True)
    description = models.TextField(null=False, blank=False)

    @property
    def topics(self):
        return self.get_topics()

    def get_topics(self) -> models.QuerySet['SyllabiTopic']:
        return self.syllabitopic_set.all()

    def get_next_order(self):
        last = self.get_topics().last()
        if last:
            return last.order + 1
        return 1

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = get_unique_slug(self.title, self)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ['order']


class SyllabiTopic(models.Model):
    """Syllabi Topic Model"""

    syllabi = models.ForeignKey(
        CurriculumSyllabi, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)
    title = models.CharField(max_length=255, null=False,
                             blank=False)
    slug = models.SlugField(max_length=255, null=True,
                            blank=True, unique=True)
    description = models.TextField(null=False, blank=False)
    resources = models.ManyToManyField('Resource.Resource', blank=True)

    def get_quizzes(self) -> models.QuerySet[Quiz]:
        return self.quiz_set.all()

    @property
    def quiz(self):
        return self.get_quizzes()

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = get_unique_slug(self.title, self)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ['order']


class CurriculumEnrollment(models.Model):
    """Curriculum Enrollment Model"""

    curriculum = models.ForeignKey(
        Curriculum, on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    progress = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    completed = models.BooleanField(default=False)

    @property
    def completed_weeks(self):
        syllabus = self.curriculum.get_syllabus()

        def count(prev: int, syllabi: CurriculumSyllabi):
            """
            Count completed syllabus
            """
            is_completed = SyllabiProgress.objects.syllabi_completed(
                self, syllabi
            )
            return prev + 1 if is_completed else prev
        return reduce(count, syllabus, 0)

    def __str__(self) -> str:
        return f"{self.user.email} - {self.curriculum.name}"


class SyllabiProgress(models.Model):
    """Curriculum Progress Model"""

    enrollment = models.ForeignKey(
        CurriculumEnrollment, on_delete=models.CASCADE)
    syllabi = models.ForeignKey(
        CurriculumSyllabi, on_delete=models.CASCADE)
    topic = models.ForeignKey(
        SyllabiTopic, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    quiz_mark = models.PositiveIntegerField(default=0)
    last_attempted = models.DateTimeField(null=True)
    objects = SyllabiProgressManager()


class CurriculumReview(models.Model):
    """Curriculum Review Model"""

    SENTIMENT = (
        ('POS', 'Positive'),
        ('NEG', 'Negative'),
        ('NEU', 'Neutral'),
    )

    LABEL = (
        ('A', 'Course Content'),
        ('B', 'Exercises'),
        ('C', 'Course Structure'),
        ('D', 'Learning Experience'),
        ('E', 'Support'),
    )

    enrollment = models.ForeignKey(
        CurriculumEnrollment, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    review = models.TextField(null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sentiment = models.CharField(
        max_length=3, null=True, blank=True,
        choices=SENTIMENT
    )
    label = models.CharField(
        max_length=1, choices=LABEL, null=True, blank=True)


@receiver(pre_save, sender=CurriculumSyllabi)
def set_syllabi_order(sender, instance, **kwargs):
    if not instance.id and instance.order == 0:
        instance.order = instance.curriculum.get_next_order()


@receiver(pre_save, sender=SyllabiTopic)
def set_topic_order(sender, instance, **kwargs):
    if not instance.id and instance.order == 0:
        instance.order = instance.syllabi.get_next_order()


@receiver(pre_save, sender=SyllabiProgress)
def set_enrollment_progress(sender, instance: SyllabiProgress, **kwargs):
    enrollment = instance.enrollment
    all_syllabi = SyllabiProgress.objects.filter(
        enrollment=enrollment
    )
    completed_syllabi = all_syllabi.filter(completed=True)
    enrollment.progress = round(
        (completed_syllabi.count() / all_syllabi.count()) * 100, 2)
    enrollment.save()
