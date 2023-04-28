from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify


class Curriculum(models.Model):
    """Curriculum Model"""

    DIFFICULTY = (
        ('B', 'Beginner'),
        ('I', 'Intermediate'),
        ('A', 'Advanced'),
    )

    name = models.CharField(max_length=255, null=False,
                            blank=False, unique=True)
    slug = models.SlugField(max_length=255, null=True, blank=True)
    description = models.TextField(null=False, blank=False)
    objective = models.TextField(null=False, blank=False)
    prerequisites = models.TextField(null=False, blank=False)
    enrolled = models.IntegerField(default=0)
    difficulty = models.CharField(
        choices=DIFFICULTY, max_length=1, null=False, blank=False)
    resources = models.ManyToManyField('Resource.Resource', blank=True)
    rating = models.FloatField(default=0.0)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Curriculum, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class CurriculumSyllabi(models.Model):
    """Curriculum Syllabi Model"""

    curriculum = models.ForeignKey(
        Curriculum, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)
    title = models.CharField(max_length=255, null=False, blank=False)
    slug = models.SlugField(max_length=255, null=True, blank=True, unique=True)
    description = models.TextField(null=False, blank=False)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(CurriculumSyllabi, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ['order']


class SyllabiTopic(models.Model):
    """Syllabi Topic Model"""

    syllabi = models.ForeignKey(
        CurriculumSyllabi, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)
    title = models.CharField(max_length=255, null=False, blank=False)
    slug = models.SlugField(max_length=255, null=True, blank=True, unique=True)
    description = models.TextField(null=False, blank=False)
    resources = models.ManyToManyField('Resource.Resource', blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(SyllabiTopic, self).save(*args, **kwargs)

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


class CurriculumReview(models.Model):
    """Curriculum Review Model"""

    SENTIMENT = (
        ('P', 'Positive'),
        ('N', 'Negative'),
        ('N', 'Neutral'),
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
    sentiment = models.CharField(max_length=255, null=True, blank=True)
    label = models.CharField(
        max_length=1, choices=LABEL, null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.user.email} - {self.curriculum.name}"
