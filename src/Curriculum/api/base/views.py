from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from Curriculum.models import Curriculum

from . import serializers


class CurriculumList(generics.ListAPIView):
    permission_classes = []
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
    permission_classes = []
    serializer_class = serializers.SingleCurriculumSerializer
    lookup_field = 'id'

    def get_queryset(self):
        return Curriculum.objects.all()


    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
