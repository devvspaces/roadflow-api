from rest_framework import serializers

from Curriculum.models import (Curriculum, CurriculumSyllabi, SyllabiProgress,
                               SyllabiTopic)
from Resource.models import Resource


class SyllabiTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = SyllabiTopic
        exclude = ["resources"]


class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        exclude = []


class SyllabiTopicWithResourcesSerializer(serializers.ModelSerializer):
    resources = ResourceSerializer(many=True)

    class Meta:
        model = SyllabiTopic
        exclude = []


class CurriculumSyllabiSerializer(serializers.ModelSerializer):
    outlines = serializers.SerializerMethodField()
    topics = SyllabiTopicSerializer(many=True)

    class Meta:
        model = CurriculumSyllabi
        exclude = []

    def get_outlines(self, obj):
        topics = obj.syllabitopic_set.all()
        return [topic.title for topic in topics]


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


class EnrolledSingleCurriculumSerializer(CurriculumSerializer):
    syllabus = serializers.SerializerMethodField()

    def get_syllabus(self, obj: Curriculum):
        enrollment = self.context.get("enrolloment")
        syllabus = []

        for syllabi in obj.get_syllabus():
            completed = SyllabiProgress.objects.syllabi_completed(
                enrollment, syllabi)
            data = CurriculumSyllabiSerializer(instance=syllabi).data
            data['completed'] = completed
            syllabus.append(data)

        return syllabus


class SyllabiProgressSerializer(serializers.ModelSerializer):
    syllabi = CurriculumSyllabiSerializer()
    topic = SyllabiTopicWithResourcesSerializer()

    class Meta:
        model = SyllabiProgress
        exclude = ["enrollment"]


class CurriculumEnrollSerializer(serializers.Serializer):
    curriculum = serializers.CharField()

    def validate_curriculum(self, val):
        try:
            curriculum = Curriculum.objects.get(slug=val)
            user = self.context.get('request').user

            # Check if user is already enrolled
            if user.has_enrolled_curriculum(curriculum):
                raise serializers.ValidationError(
                    "Already enrolled in this curriculum")

        except Curriculum.DoesNotExist:
            raise serializers.ValidationError(
                "Curriculum does not exist")

        return curriculum


class CheckEnrolledSerializer(serializers.Serializer):
    curriculum = serializers.CharField()

    def validate_curriculum(self, val):
        try:
            curriculum = Curriculum.objects.get(slug=val)
            user = self.context.get('request').user

            if not user.has_enrolled_curriculum(curriculum):
                raise serializers.ValidationError(
                    "Not enrolled in this curriculum")

        except Curriculum.DoesNotExist:
            raise serializers.ValidationError(
                "Curriculum does not exist")

        return curriculum
