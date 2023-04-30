from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from account.api.base.tokens import TokenGenerator
from account.models import User
from utils.base.general import get_tokens_for_user

from . import serializers
from .utils import send_password_reset_email, send_verification_email


class RegisterAPIView(generics.CreateAPIView):
    """
    Register a new user and
    send a verification email to user.
    """
    permission_classes = []
    serializer_class = serializers.RegisterSerializer

    @swagger_auto_schema(
        responses={201: serializers.UserSerializer}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user_serializer = serializers.UserSerializer(user)
        send_verification_email(user, request)
        return Response(
            data=user_serializer.data,
            status=status.HTTP_201_CREATED
        )


class ValidateRegistrationOtpView(generics.GenericAPIView):
    """
    Validate the otp sent to user's email.
    """
    permission_classes = []
    serializer_class = serializers.ValidateRegistrationOtpSerializer

    @swagger_auto_schema(
        responses={200: serializers.UserSerializer}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user_serializer = serializers.UserSerializer(user)
        return Response(
            data=user_serializer.data,
            status=status.HTTP_201_CREATED
        )


class TokenRefreshAPIView(generics.GenericAPIView):
    serializer_class = serializers.TokenRefreshSerializer
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class LoginAPIView(generics.GenericAPIView):
    serializer_class = serializers.LoginSerializer
    permission_classes = []

    @swagger_auto_schema(
        responses={
            200: serializers.LoginResponseSerializer200,
        }
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get('email')
        user: User = User.objects.get(email=email)
        if user.verified_email:
            user_details = serializers.UserSerializer(user).data
            response_data = {
                'tokens': get_tokens_for_user(user),
                'user': user_details
            }
            return Response(data=response_data)

        send_verification_email(user, request)
        return Response(
            data={
                "email": ['Please verify your email first.'],
                "euid": "email_not_verified"
            }, status=status.HTTP_400_BAD_REQUEST
        )


class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = serializers.ChangePasswordSerializer
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def get_object(self):
        return self.request.user

    def get_queryset(self):
        return User.objects.filter(active=True)


class RequestForgetPasswordView(generics.GenericAPIView):
    """
    Request a password reset email (otp).

    Otp is sent to user's email.
    """

    serializer_class = serializers.RequestForgetPasswordSerializer
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        send_password_reset_email(serializer.user, request)
        return Response(data=serializer.data)


class ValidateForgetPasswordOtpView(generics.GenericAPIView):
    """
    Validate the forget password otp sent to user's email.

    Return a token to be used for resetting password.
    """
    permission_classes = []
    serializer_class = serializers.ValidateOtpSerializer

    @swagger_auto_schema(
        responses={200: serializers.ForgetPasswordTokenSerializer}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Create a token for user to reset password
        generator = TokenGenerator()
        user = serializer.validated_data['email']
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = generator.make_token(user)
        # uidb64 and token are used to identify the user

        return Response(
            data={
                'uidb64': uidb64,
                'token': token
            },
            status=status.HTTP_201_CREATED
        )


class ForgetPasswordView(generics.GenericAPIView):
    """
    Reset password using the token received by validating the otp.

    User password will be reset to the new password.
    Returns a new access and refresh token including user details.
    """
    serializer_class = serializers.ForgetPasswordSerializer
    permission_classes = []

    @swagger_auto_schema(
        responses={
            200: serializers.LoginResponseSerializer200,
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user_details = serializers.UserSerializer(user).data
        response_data = {
            'tokens': get_tokens_for_user(user),
            'user': user_details
        }
        return Response(data=response_data)


class UserRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = serializers.UserSerializer

    def get_object(self):
        return self.request.user

    def get_queryset(self):
        return User.objects.filter(active=True)
