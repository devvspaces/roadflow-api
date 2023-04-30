from django.db.models import Manager, QuerySet


class SyllabiProgressQuery(QuerySet):

    def syllabi_completed(self, enrollment, syllabi):
        qset = self.filter(syllabi=syllabi, enrollment=enrollment)
        completed = qset.filter(completed=True).count()
        return completed == qset.count()

    def get_by_enrollment_topic(self, enrollment, topic):
        return self.get(topic=topic, enrollment=enrollment)


class SyllabiProgressManager(Manager):
    def get_queryset(self):
        return SyllabiProgressQuery(model=self.model, using=self._db)

    def syllabi_completed(self, enrollment, syllabi):
        return self.get_queryset().syllabi_completed(enrollment, syllabi)

    def get_by_enrollment_topic(self, enrollment, topic):
        return self.get_queryset().get_by_enrollment_topic(enrollment, topic)

    def get_by_user_and_topic(self, user, topic_slug):
        qset = self.get_queryset()
        return qset.get(enrollment__user=user, topic__slug__exact=topic_slug)
