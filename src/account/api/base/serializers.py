from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.password_validation import validate_password
from django.db.transaction import atomic
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.utils.text import slugify
from firebase_admin.auth import (ExpiredIdTokenError, InvalidIdTokenError,
                                 RevokedIdTokenError, UserDisabledError)
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from account.api.base.tokens import TokenGenerator
from account.models import Profile, User
from utils.base.firebase import FirebaseProvider
from utils.base.general import get_access_time, random_text
from utils.base.github import get_github_account
from utils.base.logger import err_logger


class JWTTokenValidateSerializer(serializers.Serializer):
    token = serializers.CharField()


class TokenRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField(
        help_text=f"Refresh token will be used to generate new \
access token every {settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']} minutes ",
        write_only=True,
        required=True,
    )
    access = serializers.ReadOnlyField()
    access_expires_at = serializers.IntegerField(
        help_text="Access token expires at", read_only=True
    )

    def validate(self, attrs):
        refresh = RefreshToken(attrs["refresh"])

        data = {"access": str(refresh.access_token)}
        api_settings = getattr(settings, "SIMPLE_JWT", None)

        if not api_settings:
            raise Exception("SIMPLE_JWT settings not found")

        # Get the access token lifetime
        data["access_expires_at"] = get_access_time()
        return data


class JWTTokenResponseSerializer(serializers.Serializer):
    refresh = serializers.CharField(
        help_text=f"Refresh token will be used to generate new \
access token every {settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']} minutes "
    )
    access = serializers.CharField(help_text="Used in headers to authenticate users")
    refresh_expires_at = serializers.IntegerField(help_text="Refresh token expires at")
    access_expires_at = serializers.IntegerField(help_text="Access token expires at")


class TokenGenerateSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class TokenGenerateSerializerEmail(serializers.Serializer):
    email = serializers.EmailField(
        help_text="Email of user to verify and return tokens for"
    )


class LoginGoogleSerializer(serializers.Serializer):
    id_token = serializers.CharField(
        help_text="Google id token to verify and return tokens for"
    )

    def validate_id_token(self, value):
        try:
            data = FirebaseProvider.verify_token(value)
        except InvalidIdTokenError:
            raise serializers.ValidationError("Invalid token")
        except ExpiredIdTokenError:
            raise serializers.ValidationError("Token has expired")
        except RevokedIdTokenError:
            raise serializers.ValidationError("Token has been revoked")
        except UserDisabledError:
            raise serializers.ValidationError("User has been disabled")
        except Exception as e:
            err_logger.exception(e)
            err_logger.error(f"Error verifying token: {value}")
            raise serializers.ValidationError("Error verifying token")
        return data

    def save(self) -> User:
        with atomic():
            data = self.validated_data["id_token"]
            email = data["email"]
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                # Get a unique username
                username = slugify(email.split("@")[0]) + random_text()
                user = User.objects.create_user(email=email, username=username)
            if not user.verified_email:
                user.verified_email = True
                user.save()

            # Update profile missing data
            if not user.profile.fullname:
                user.profile.fullname = data.get("name", "")
            if not user.profile.image:
                user.profile.image = data.get("picture", "")
            user.profile.save()
            return user


class LoginGithubSerializer(LoginGoogleSerializer):
    access_token = serializers.CharField(
        help_text="Github access token to get github account details and email"
    )

    def save(self) -> User:
        with atomic():
            data = self.validated_data["id_token"]
            access_token = self.validated_data["access_token"]
            account, primary_email = get_github_account(access_token)

            if primary_email:
                email = primary_email["email"]
            else:
                github_com = data["firebase"]["identities"]["github.com"]
                if github_com:
                    uid = github_com[0]
                else:
                    uid = data["auth_time"]
                email = f"{uid}+{account['login']}@noreply.roadflowai.com"

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                username = account["login"]
                try:
                    User.objects.get(username=username)
                    username = email.split("@")[0]
                except User.DoesNotExist:
                    pass
                user = User.objects.create_user(email=email, username=username)

            # Update profile missing data
            if not user.verified_email and primary_email and primary_email["verified"]:
                user.verified_email = True
                user.save()
            if not user.profile.fullname:
                user.profile.fullname = data.get("name", "")
            if not user.profile.image:
                user.profile.image = data.get("picture", "")
            if not user.profile.bio:
                user.profile.bio = account["bio"]
            if not user.profile.github:
                user.profile.github = account["html_url"]
            if account["twitter_username"] and not user.profile.twitter:
                user.profile.twitter = f"https://x.com/{account['twitter_username']}"
            user.profile.save()
            return user

class LoginTwitterSerializer(LoginGoogleSerializer):
    def save(self) -> User:
        with atomic():
            data = self.validated_data["id_token"]
            email = data['email']

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                username = data["name"]
                try:
                    User.objects.get(username=username)
                    username = username + random_text()
                except User.DoesNotExist:
                    pass
                user = User.objects.create_user(email=email, username=username)

            # Update profile missing data
            if not user.verified_email and data["email_verified"]:
                user.verified_email = True
                user.save()
            if not user.profile.fullname:
                user.profile.fullname = data.get("name", "")
            if not user.profile.image:
                user.profile.image = data.get("picture", "")
            user.profile.save()
            return user


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )

    class Meta:
        model = User
        fields = ("password", "email", "username")

    def create(self, validated_data):
        email = validated_data.get("email")
        password = validated_data.get("password")
        username = validated_data.get("username")
        user = User.objects.create_user(
            email=email, password=password, username=username
        )
        return user


class ValidateOtpSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True)

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist")
        return user

    def validate(self, attrs):
        otp = attrs["otp"]
        user: User = attrs["email"]

        if not user.validate_otp(otp):
            raise serializers.ValidationError({"otp": "Invalid otp"})

        return attrs


class ForgetPasswordTokenSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    uidb64 = serializers.CharField(required=True)


class ValidateRegistrationOtpSerializer(ValidateOtpSerializer):
    def save(self, **kwargs):
        user: User = self.validated_data["email"]
        user.verified_email = True
        user.save()


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        # Get required info for validation
        email = attrs["email"]
        password = attrs["password"]

        """
        Check that the email is available in the User table
        """
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"email": "Please provide a valid email and password"}
            )

        if not user.check_password(password):
            raise serializers.ValidationError(
                {"email": "Please provide a valid email and password"}
            )

        return attrs


class ProfileSerializer(serializers.ModelSerializer):
    fullname = serializers.CharField(read_only=True)

    class Meta:
        model = Profile
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ("email", "username", "profile")

    def validate_phoneno(self, value):
        if value:
            # Check if this phone has been used by anyone
            qset = User.objects.filter(phone=value)

            if self.instance:
                qset = qset.exclude(pk=self.instance.pk)

            exists = qset.exists()
            if exists:
                raise serializers.ValidationError(
                    "This phone number has already been used"
                )

        return value


class ForgetPasswordSerializer(serializers.Serializer):
    uidb64 = serializers.CharField(required=True)
    token = serializers.CharField(required=True)
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )

    def validate(self, attrs):
        """
        Validate the token and uidb64
        """
        uidb64 = attrs["uidb64"]
        token = attrs["token"]

        User = get_user_model()
        user = None

        try:
            uidb64 = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=uidb64)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError("Invalid token")

        generator = TokenGenerator()
        if not generator.check_token(user, token):
            raise serializers.ValidationError("Invalid token")

        attrs["user"] = user
        return attrs

    def save(self, **kwargs):
        # Get the user
        user: User = self.validated_data["user"]
        password = self.validated_data["password"]

        # Set password
        user.set_password(password)
        user.save()

        return user


class RequestForgetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    # Store the user instance
    user: AbstractBaseUser = None

    def validate_email(self, value):
        try:
            self.user: User = User.objects.get(email=value)
            if not self.user.verified_email:
                raise serializers.ValidationError("Please verify your email first")
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist")
        return value


class ChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    instance: AbstractBaseUser = None

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "old_password",
            "new_password",
        )
        extra_kwargs = {
            "email": {"read_only": True},
        }

    def validate(self, attrs):
        if not self.instance.check_password(attrs["old_password"]):
            raise serializers.ValidationError(
                {"old_password": "Old password is not correct"}
            )
        return attrs

    def update(self, instance, validated_data):
        # Set password
        new_password = validated_data.get("new_password")
        instance.set_password(new_password)
        instance.save()

        return instance


class LoginResponseSerializer200(serializers.Serializer):
    user = UserSerializer()
    tokens = JWTTokenResponseSerializer()
