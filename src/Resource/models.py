from django.db import models


class Resource(models.Model):

    TYPE = (
        ('C', 'Course'),
        ('A', 'Article'),
        ('B', 'Book'),
        ('V', 'Video'),
        ('O', 'Other'),
    )

    name = models.CharField(max_length=255, null=False, blank=False)
    url = models.URLField(null=False, blank=False)
    description = models.TextField(null=True, blank=True)
    author = models.CharField(max_length=255, null=True, blank=True)
    rtype = models.CharField(
        max_length=1, choices=TYPE, null=False, blank=False)
    provider = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self) -> str:
        return self.name
