from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings


class JobRole(models.Model):
    """Job Role Model"""

    name = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(null=False, blank=False)
    min_salary = models.DecimalField(
        max_digits=10, decimal_places=2, null=False, blank=False)
    max_salary = models.DecimalField(
        max_digits=10, decimal_places=2, null=False, blank=False)
    video_url = models.URLField(null=True, blank=True)
    in_demand = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name


class Roadmap(models.Model):
    """
    Road Map Model
    """

    job_role = models.ForeignKey(
        JobRole, on_delete=models.DO_NOTHING, null=True)

    def __str__(self) -> str:
        if self.job_role:
            return f"Roadmap for {self.job_role.name}"
        return "Roadmap (NULL)"


class RoadmapCurriculum(models.Model):
    """
    Roadmap Curriculum Model
    """

    TYPE = (
        ('R', 'Required'),
        ('E', 'Elective'),
    )

    roadmap = models.ForeignKey(
        Roadmap, on_delete=models.CASCADE)
    curriculum = models.ForeignKey(
        'Curriculum.Curriculum', on_delete=models.CASCADE)
    order = models.IntegerField(default=0)
    rtype = models.CharField(
        max_length=1, choices=TYPE, null=False, blank=False)

    class Meta:
        ordering = ['order']


class RoadmapEnrollment(models.Model):
    """
    Roadmap Enrollment Model
    """

    roadmap = models.ForeignKey(
        Roadmap, on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    progress = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
