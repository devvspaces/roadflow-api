from django.urls import path

from . import views

app_name = 'curriculum'
urlpatterns = [
    path('', views.CurriculumList.as_view(), name='list-curriculum'),
]
