from django.conf import settings
from django.db import models


class UserFeedback(models.Model):
    """Curriculum Review Model"""

    SENTIMENT = (
        ('P', 'Positive'),
        ('N', 'Negative'),
        ('N', 'Neutral'),
    )
    SENTIMENT_REV_LOOKUP = {v: k for k, v in dict(SENTIMENT).items()}
    
    LABEL = (
        ('A', 'Course Content'),
        ('B', 'Exercises'),
        ('C', 'Course Structure'),
        ('D', 'Learning Experience'),
        ('E', 'Feature Request'),
        ('F', 'Improvement'),
    )
    LABEL_REV_LOOKUP = {v: k for k, v in dict(LABEL).items()}

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE)
    review = models.TextField(null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sentiment = models.CharField(max_length=255, null=True, blank=True)
    label = models.CharField(
        max_length=1, choices=LABEL, null=True, blank=True)
