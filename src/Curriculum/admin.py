from django.contrib import admin

from Quiz.models import Quiz

from .models import (Curriculum, CurriculumEnrollment, CurriculumReview,
                     CurriculumSyllabi, SyllabiProgress, SyllabiTopic)


class CurriculumSyllabiInline(admin.StackedInline):
    model = CurriculumSyllabi


@admin.register(Curriculum)
class CurriculumAdmin(admin.ModelAdmin):
    inlines = [
        CurriculumSyllabiInline
    ]


class SyllabiTopicInline(admin.StackedInline):
    model = SyllabiTopic


@admin.register(CurriculumSyllabi)
class CurriculumSyllabiAdmin(admin.ModelAdmin):
    inlines = [
        SyllabiTopicInline
    ]


class QuizInline(admin.StackedInline):
    model = Quiz


@admin.register(SyllabiTopic)
class SyllabiTopicAdmin(admin.ModelAdmin):
    inlines = [
        QuizInline
    ]


admin.site.register([
    CurriculumEnrollment,
    SyllabiProgress,
    CurriculumReview
])
