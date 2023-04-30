from django.db import models


class Quiz(models.Model):
    """Quiz model will be connect"""
    question = models.CharField(max_length=255, null=False, blank=False)
    topic = models.ForeignKey(
        'Curriculum.SyllabiTopic', on_delete=models.CASCADE)

    def get_options(self) -> models.QuerySet['QOption']:
        return self.qoption_set.all()

    @property
    def options(self):
        return self.get_options()


class QOption(models.Model):
    """QOption model will be connect"""
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    option = models.CharField(max_length=255, null=False, blank=False)
    reason = models.TextField(null=True, blank=True)
    is_correct = models.BooleanField(default=False)
