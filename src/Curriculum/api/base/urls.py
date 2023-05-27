from django.urls import path

from . import views

app_name = 'curriculum'
urlpatterns = [
    path('', views.CurriculumList.as_view(), name='list-curriculum'),
    path(
        'upcoming-events/',
        views.GetUpcomingEvents.as_view(),
        name='upcoming-events'),
    path(
        'enrolled/', views.GetEnrolledCurriculums.as_view(),
        name='get-enrolled-curriculums'),
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
    path(
        'topic/quiz/<slug:slug>/', views.GetTopicQuiz.as_view(),
        name='get-syllabi-topic-quiz'),
    path(
        'topic/quiz/submit/<slug:slug>/', views.SubmitTopicQuiz.as_view(),
        name='submit-syllabi-topic-quiz'),
    path(
        'resources/<slug:slug>/',
        views.GetCurriculumWithResources.as_view(),
        name='get-curriculum-resources'),
    path(
        'grades/<slug:slug>/',
        views.GetEnrolledCurriculumGrades.as_view(),
        name='get-curriculum-grades'),
    path(
        'submit-review/<slug:slug>/',
        views.RateCurriculum.as_view(),
        name='submit-review'),
]
