from typing import Dict

from django.conf import settings
from django.http import HttpResponseBadRequest, HttpResponseNotFound
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.response import Response

from Curriculum.models import Curriculum, SyllabiProgress, SyllabiTopic
from Quiz.models import QOption, Quiz
from utils.base.date import dt_now
from utils.base.mindsdb import classify_text, sentiment_text
from utils.base.showwcase import show_get

from . import serializers


class CurriculumList(generics.ListAPIView):
    serializer_class = serializers.CurriculumSerializer

    def get_queryset(self):
        search = self.request.GET.get('search', None)
        queryset = Curriculum.objects.all()
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset

    @swagger_auto_schema(
        query_serializer=serializers.SearchQuerySerializer
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class SingleCurriculum(generics.RetrieveAPIView):
    serializer_class = serializers.SingleCurriculumSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        return Curriculum.objects.all()


class EnrolledSingleCurriculum(generics.RetrieveAPIView):
    serializer_class = serializers.EnrolledSingleCurriculumSerializer
    lookup_field = 'slug'

    def get_serializer_context(self):
        data = super().get_serializer_context()
        return {
            **data,
            "enrolloment": self.request.user
            .get_curriculum_enrollment(self.get_object())
        }

    def get_queryset(self):
        return Curriculum.objects.all()

    @swagger_auto_schema(
        responses={
            200: serializers.EnrolledSingleCurriculumSerializer
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class GetEnrolledCurriculums(generics.ListAPIView):
    serializer_class = serializers.CurriculumEnrollmentSerializer

    def get_queryset(self):
        return self.request.user.get_curriculum_enrollments()


class GetSyllabiProgress(generics.RetrieveAPIView):
    serializer_class = serializers.SyllabiProgressSerializer
    lookup_field = 'slug'

    def get_object(self):
        topic = super().get_object()
        curriculum = topic.syllabi.curriculum
        enrollment = self.request.user\
            .get_curriculum_enrollment(curriculum)
        return SyllabiProgress.objects.get_by_enrollment_topic(
            enrollment, topic
        )

    def get_queryset(self):
        return SyllabiTopic.objects.all()


class EnrollCurriculum(generics.GenericAPIView):
    serializer_class = serializers.CurriculumEnrollSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        curriculum = serializer.validated_data.get('curriculum')
        request.user.enroll_curriculum(curriculum)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CheckEnrolled(generics.GenericAPIView):
    """
    Check if a user is enrolled in a curriculum
    """
    serializer_class = serializers.CheckEnrolledSerializer
    lookup_url_kwarg = "slug"

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(data={
            'curriculum': kwargs.get(self.lookup_url_kwarg)
        })
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class GetTopicQuiz(generics.RetrieveAPIView):
    serializer_class = serializers.TopicQuizSerializer
    lookup_field = "slug"

    def get_quiz_mark(self):
        """
        Get the mark of the quiz if it exists
        """
        try:
            syllabi_progress: SyllabiProgress = SyllabiProgress.objects\
                .get_by_user_and_topic(
                    self.request.user, self.kwargs.get(self.lookup_field)
                )
        except SyllabiProgress.DoesNotExist:
            return HttpResponseNotFound("Quiz does not exists")

        rem_time = 0
        if syllabi_progress.last_attempted:
            rem_time = (
                dt_now() - syllabi_progress.last_attempted).seconds
            rem_time = settings.TEST_INTERVAL_SECONDS - rem_time

        return {
            "completed": syllabi_progress.completed,
            "mark": syllabi_progress.quiz_mark,
            "remaining_time": max(rem_time, 0)
        }

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        quiz_mark = self.get_quiz_mark()
        if isinstance(quiz_mark, HttpResponseNotFound):
            return quiz_mark

        serializer_class = self.get_serializer_class()
        serializer = serializer_class(
            instance, context={
                "request": request,
                "quiz_mark": quiz_mark
            }
        )
        return Response(serializer.data)

    def get_queryset(self):
        return SyllabiTopic.objects.all()


class SubmitTopicQuiz(generics.GenericAPIView):
    lookup_url_kwarg = "slug"

    def validate_request(self):
        if not self.request.data:
            return HttpResponseBadRequest

        try:
            syllabi_progress: SyllabiProgress = SyllabiProgress.objects\
                .get_by_user_and_topic(
                    self.request.user, self.kwargs.get(self.lookup_url_kwarg)
                )
        except SyllabiProgress.DoesNotExist:
            return HttpResponseNotFound("Quiz does not exists")

        if syllabi_progress.last_attempted:
            diff = dt_now() - syllabi_progress.last_attempted
            print(diff.total_seconds())
            if (diff.total_seconds() < settings.TEST_INTERVAL_SECONDS):
                return Response("Time interval for \
test retake not reached", status=status.HTTP_400_BAD_REQUEST)

        return syllabi_progress

    @swagger_auto_schema(
        request_body=serializers.SubmitQuizOptionSerializer(),
        responses={
            200: serializers.SubmitQuizMarkResponseSerializer
        }
    )
    def post(self, request, *args, **kwargs):
        """
        Return List of QSelections as response
        """
        syllabi_progress = self.validate_request()
        if type(syllabi_progress) != SyllabiProgress:
            return syllabi_progress

        data: Dict[str, str] = request.data
        quizzes = syllabi_progress.topic.get_quizzes()
        mark = 0
        total = 0
        quiz_response = []

        for quiz_id, option_id in data.items():
            if (not quiz_id.isdigit()) or (not option_id.isdigit()):
                return Response(
                    "Invalid quiz question or option",
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                quiz = quizzes.get(id=int(quiz_id))
                option = quiz.get_options().get(id=int(option_id))
            except (Quiz.DoesNotExist, QOption.DoesNotExist):
                return Response(
                    "Quiz question or option does not exist",
                    status=status.HTTP_400_BAD_REQUEST
                )

            if option.is_correct:
                mark += 1
            total += 1
            quiz_response.append({
                quiz_id: {
                    "selected": option_id,
                    "is_correct": option.is_correct,
                    "reason": option.reason,
                }
            })

        syllabi_progress.quiz_mark = round((mark / total) * 100, 2)
        syllabi_progress.last_attempted = dt_now()
        syllabi_progress.completed = True
        syllabi_progress.save()

        data = {
            "quiz": quiz_response,
            "mark": syllabi_progress.quiz_mark,
            "remaining_time": settings.TEST_INTERVAL_SECONDS
        }
        return Response(data)


class GetCurriculumWithResources(generics.RetrieveAPIView):
    serializer_class = serializers.CurriculumWithResourcesSerializer
    lookup_field = "slug"

    def get_serializer_context(self):
        data = super().get_serializer_context()
        return {
            **data,
            "enrolloment": self.request.user
            .get_curriculum_enrollment(self.get_object())
        }

    def get_queryset(self):
        return Curriculum.objects.all()

    @swagger_auto_schema(
        responses={
            200: serializers.CurriculumWithResourcesSerializer
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class GetEnrolledCurriculumGrades(generics.RetrieveAPIView):
    serializer_class = serializers.SyllabiProgressWithoutTopicSerializer
    lookup_field = "slug"

    def get_queryset(self):
        return Curriculum.objects.all()

    @swagger_auto_schema(
        responses={
            200: serializers.SPWTCRSerializer
        }
    )
    def get(self, request, *args, **kwargs):
        cur = self.get_object()
        enrollment = self.request.user.get_curriculum_enrollment(
            cur)
        syllabus_progress = SyllabiProgress.objects.filter(
            enrollment=enrollment)
        responses = []
        for syllabi_progress in syllabus_progress:
            data = serializers.SyllabiProgressWithoutTopicSerializer(
                instance=syllabi_progress).data
            responses.append(data)

        data = {
            "curriculum": serializers.EnrolledSingleCurriculumSerializer(
                instance=cur).data,
            "progress": responses
        }
        return Response(data)


class RateCurriculum(generics.CreateAPIView):
    serializer_class = serializers.ReviewSerializer
    lookup_field = "slug"

    def get_queryset(self):
        return Curriculum.objects.all()

    def get_object(self):
        return self.get_queryset().get(
            slug=self.kwargs.get(self.lookup_field)
        )

    def get_serializer_context(self):
        data = super().get_serializer_context()
        cur = self.get_object()
        enrollment = self.request.user\
            .get_curriculum_enrollment(cur)
        return {
            **data,
            "enrollment": enrollment
        }

    def perform_create(self, serializer):
        cur = self.get_object()
        enrollment = self.request.user\
            .get_curriculum_enrollment(cur)
        review = serializer.save(enrollment=enrollment)

        # Classify review here, in live app use cron job
        review.sentiment = sentiment_text(review.review)
        review.label = classify_text(review.review)
        review.save()

    @swagger_auto_schema(
        responses={
            201: serializers.ReviewSerializer
        },
        request_body=serializers.ReviewSerializer
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class GetUpcomingEvents(generics.ListAPIView):
    serializer_class = serializers.EventSerializer
    permission_classes = []

    def get_queryset(self):
        results = show_get("/events/upcoming")
        if not results:
            results = []

        def _mapper(data):
            return {
                "title": data.get("name"),
                "start": data.get("start_date"),
                "end": data.get("end_date"),
                "url": data.get("project").get("_self"),
                "upvotes": data.get("project").get("totalUpvotes"),
                "views": data.get("project").get("totalViews"),
                "reading_time": data.get("project")
                .get("readingStats").get("text"),
                "image": data.get("project").get("coverImageUrl"),
                "projectSummary": data.get("project").get("projectSummary"),
            }

        return list(map(_mapper, results))

    @method_decorator(cache_page(settings.SHOWWCASE_API_CACHE_TIME))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
