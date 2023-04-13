from django.urls import path

from . import views

app_name = 'auth'
urlpatterns = [
    path('register/', views.RegisterAPIView.as_view(), name='register'),
    path('login/', views.LoginAPIView.as_view(), name='login'),
    path('token/user/refresh/',
         views.TokenRefreshAPIView.as_view(), name='token_refresh'),
    path('token/user/validate/',
         views.TokenVerifyAPIView.as_view(), name='token_validate'),
    path('user/change-password/', views.ChangePasswordView.as_view(),
         name='change_password'),
]
