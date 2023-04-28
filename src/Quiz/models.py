from django.db import models


class Quiz(models.Model):
    """Quiz model will be connect"""
    question = models.CharField(max_length=255, null=False, blank=False)
    topic = models.ForeignKey(
        'Curriculum.SyllabiTopic', on_delete=models.CASCADE)


class QOption(models.Model):
    """QOption model will be connect"""
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    option = models.CharField(max_length=255, null=False, blank=False)
    reason = models.TextField(null=True, blank=True)
    is_correct = models.BooleanField(default=False)


class QSelection(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    selected = models.ForeignKey(QOption, on_delete=models.CASCADE)
    topic_progress = models.ForeignKey(
        'Curriculum.SyllabiProgress', on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)
