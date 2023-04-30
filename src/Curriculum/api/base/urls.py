from django.urls import path

from . import views

app_name = 'curriculum'
urlpatterns = [
    path('', views.CurriculumList.as_view(), name='list-curriculum'),
    path(
        'enroll/', views.EnrollCurriculum.as_view(),
        name='enroll-curriculum'),
    path(
        '<slug:slug>/', views.SingleCurriculum.as_view(),
        name='get-curriculum'),
    path(
        'check-enrolled/<slug:slug>/', views.CheckEnrolled.as_view(),
        name='check-enrolled-curriculum'),
    path(
        'enrolled/<slug:slug>/', views.EnrolledSingleCurriculum.as_view(),
        name='get-enrolled-curriculum'),
    path(
        'topic/<slug:slug>/', views.GetSyllabiProgress.as_view(),
        name='get-syllabi-topic-progress'),
]
