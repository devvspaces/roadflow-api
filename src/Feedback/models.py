from django.db import models
from django.conf import settings


class UserFeedback(models.Model):
    """Curriculum Review Model"""

    SENTIMENT = (
        ('P', 'Positive'),
        ('N', 'Negative'),
        ('N', 'Neutral'),
    )
    LABEL = (
        ('A', 'Overall User Experience'),
        ('B', 'Customer Support'),
        ('C', 'Content Quality'),
        ('D', 'Learning Experience'),
        ('E', 'Community and Collaboration'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE)
    review = models.TextField(null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sentiment = models.CharField(max_length=255, null=True, blank=True)
    label = models.CharField(
        max_length=1, choices=LABEL, null=True, blank=True)
