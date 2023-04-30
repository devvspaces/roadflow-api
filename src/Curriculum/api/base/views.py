from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.db import transaction

from Curriculum.models import Curriculum, SyllabiProgress, SyllabiTopic

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
