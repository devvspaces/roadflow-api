from django.contrib import admin

from .models import (Curriculum, CurriculumEnrollment, CurriculumReview,
                     CurriculumSyllabi, SyllabiProgress, SyllabiTopic)

admin.site.register([
    Curriculum,
    CurriculumEnrollment,
    CurriculumSyllabi,
    SyllabiTopic,
    SyllabiProgress,
    CurriculumReview
])
