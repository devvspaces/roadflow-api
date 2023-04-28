from django.urls import path

from . import views

app_name = 'auth'
urlpatterns = [
    path('login/', views.LoginAPIView.as_view(), name='login'),
    path('register/', views.RegisterAPIView.as_view(), name='register'),
    path(
        'validate-otp/',
        views.ValidateRegistrationOtpView.as_view(), name='validate_otp'),
    path(
        'user/retrieve-update/',
        views.UserRetrieveUpdateAPIView.as_view(),
        name='user_retrieve_update'),
    path(
        'forget-password/request-reset/',
        views.RequestForgetPasswordView.as_view(),
        name='request_password_reset'),
    path(
        'forget-password/validate-otp/',
        views.ValidateForgetPasswordOtpView.as_view(),
        name='request_password_reset'),
    path(
        'forget-password/reset/',
        views.ForgetPasswordView.as_view(),
        name='password_reset'),
    path('token/user/refresh/',
         views.TokenRefreshAPIView.as_view(), name='token_refresh'),
    path('user/change-password/', views.ChangePasswordView.as_view(),
         name='change_password'),
]
