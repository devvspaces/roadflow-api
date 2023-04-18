from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

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


class ValidateForgetPasswordOtpView(generics.GenericAPIView):
    """
    Validate the forget password otp sent to user's email.

    Return a token to be used for resetting password.
    """
    permission_classes = []
    serializer_class = serializers.ValidateRegistrationOtpSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Create a token for user to reset password
        # uidb64 and token are used to identify the user

        return Response(
            data=serializer.data,
            status=status.HTTP_201_CREATED
        )


class TokenVerifyAPIView(APIView):
    """
    An authentication plugin that checks if a jwt
    access token is still valid and returns the user info.
    """

    @swagger_auto_schema(
        request_body=serializers.JWTTokenValidateSerializer,
        responses={200: serializers.UserSerializer}
    )
    def post(self, request, format=None):
        jwt_auth = JWTAuthentication()

        raw_token = request.data.get('token')

        validated_token = jwt_auth.get_validated_token(raw_token)

        user = jwt_auth.get_user(validated_token)

        serialized_user = serializers.UserSerializer(user)
        user_details = serialized_user.data

        return Response(data=user_details)


class TokenRefreshAPIView(APIView):
    serializer_class = TokenRefreshSerializer

    @swagger_auto_schema(
        request_body=TokenRefreshSerializer,
        responses={200: TokenRefreshSerializer}
    )
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
                "message": 'Please verify your email first.'
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
    serializer_class = serializers.RequestForgetPasswordSerializer
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        send_password_reset_email(serializer.user, request)
        return Response(data=serializer.data)


class ForgetPasswordView(generics.GenericAPIView):
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
        user: User = serializer.validated_data.get('user')
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
