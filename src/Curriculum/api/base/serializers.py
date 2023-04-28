from rest_framework import serializers

from Curriculum.models import Curriculum, CurriculumSyllabi


class CurriculumSyllabiSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurriculumSyllabi
        exclude = []


class SearchQuerySerializer(serializers.Serializer):
    search = serializers.CharField(
        required=False, allow_blank=True, max_length=255
    )


class CurriculumSerializer(serializers.ModelSerializer):
    weeks = serializers.SerializerMethodField()

    class Meta:
        model = Curriculum
        exclude = ['resources']

    def get_weeks(self, obj):
        return obj.curriculumsyllabi_set.all().count()


class SingleCurriculumSerializer(CurriculumSerializer):
    syllabus = CurriculumSyllabiSerializer(many=True)

    class Meta:
        model = Curriculum
        exclude = ['resources']
