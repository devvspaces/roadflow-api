from rest_framework import serializers

from Curriculum.models import (Curriculum, CurriculumEnrollment, CurriculumReview,
                               CurriculumSyllabi, SyllabiProgress,
                               SyllabiTopic)
from Quiz.models import QOption, Quiz
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


class CurriculumSyllabiWithoutTOSerializer(serializers.ModelSerializer):
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


class CurriculumWithResourcesSerializer(EnrolledSingleCurriculumSerializer):
    resources = ResourceSerializer(many=True)

    class Meta:
        model = Curriculum
        exclude = []


class SyllabiProgressSerializer(serializers.ModelSerializer):
    syllabi = CurriculumSyllabiSerializer()
    topic = SyllabiTopicWithResourcesSerializer()

    class Meta:
        model = SyllabiProgress
        exclude = ["enrollment"]


class SyllabiProgressWithoutTopicSerializer(SyllabiProgressSerializer):
    syllabi = CurriculumSyllabiWithoutTOSerializer()
    topic = SyllabiTopicSerializer()


class SPWTCRSerializer(serializers.Serializer):
    curriculum = EnrolledSingleCurriculumSerializer()
    progress = SyllabiProgressWithoutTopicSerializer(many=True)


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


class CurriculumEnrollmentSerializer(serializers.ModelSerializer):
    completed_weeks = serializers.IntegerField()
    curriculum = CurriculumSerializer()

    class Meta:
        model = CurriculumEnrollment
        exclude = ["user"]


class QOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QOption
        exclude = ['quiz']


class QuizSerializer(serializers.ModelSerializer):
    options = QOptionSerializer(many=True)

    class Meta:
        model = Quiz
        exclude = ['topic']


class TopicQuizSerializer(serializers.ModelSerializer):
    quiz = QuizSerializer(many=True)
    mark = serializers.SerializerMethodField()
    remaining_time = serializers.SerializerMethodField()
    completed = serializers.SerializerMethodField()

    class Meta:
        model = SyllabiTopic
        fields = ['quiz', 'mark', 'remaining_time', 'completed']

    def get_mark(self, obj):
        obj = self.context.get("quiz_mark")
        return obj.get('mark')

    def get_remaining_time(self, obj):
        obj = self.context.get("quiz_mark")
        return obj.get('remaining_time')

    def get_completed(self, obj):
        obj = self.context.get("quiz_mark")
        return obj.get('completed')


class SubmitQuizOptionSerializer(serializers.Serializer):
    key = serializers.CharField(help_text="Quiz id => Option id")


class SubmitQuizOptionResponseSerializer(serializers.Serializer):
    selected = serializers.CharField(help_text="Option id")
    is_correct = serializers.BooleanField()
    reason = serializers.CharField()


class SubmitQuizResponseSerializer(serializers.Serializer):
    key = SubmitQuizOptionResponseSerializer()


class SubmitQuizMarkResponseSerializer(serializers.Serializer):
    quiz = SubmitQuizResponseSerializer(many=True)
    mark = serializers.IntegerField(help_text="In percentage")
    remaining_time = serializers.IntegerField(help_text="In seconds")


class ReviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = CurriculumReview
        fields = ["rating", "review"]


class EventSerializer(serializers.Serializer):
    title = serializers.CharField()
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()
    url = serializers.CharField()
    upvotes = serializers.IntegerField()
    views = serializers.IntegerField()
    reading_time = serializers.CharField()
    image = serializers.URLField()
    projectSummary = serializers.CharField()
