from utils.base.email import render_email_message
from account.models import Profile, User
from django.shortcuts import get_object_or_404
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from utils.base.general import custom_auto_schema, get_tokens_for_user, random_otp

from . import serializers


def send_verification_email(user: User, request):
    """
    Sends a verification email to user.
    """
    message = render_email_message(
        request, 'account/email/verify_email.html',
        {
            "otp": random_otp()
        }
    )
    return user.email_user('Verify your email', message)


class RegisterAPIView(APIView):
    """
    Register a new user and
    send a verification email to user.
    """
    serializer_class = serializers.RegisterSerializer

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


class LoginAPIView(APIView):
    serializer_class = serializers.LoginSerializer

    @custom_auto_schema(
        request_body=serializers.LoginSerializer,
        responses={
            200: serializers.LoginResponseSerializer200,
        }
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get('email')
        user = User.objects.get(email=email)
        if user.verified_email:
            s2 = serializers.UserSerializer(user)
            user_details = s2.data
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

    def get_object(self):
        return self.request.user

    def get_queryset(self):
        return User.objects.filter(active=True)
