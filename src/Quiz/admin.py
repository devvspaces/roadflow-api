from django.contrib import admin

from Quiz.models import QOption, Quiz


class QOptionInline(admin.TabularInline):
    model = QOption


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    inlines = [
        QOptionInline
    ]


admin.site.register([QOption])
