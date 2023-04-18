from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from django.contrib.auth.models import AbstractBaseUser

from account.models import Profile, User


class JWTTokenValidateSerializer(serializers.Serializer):
    token = serializers.CharField()


class JWTTokenResponseSerializer(serializers.Serializer):
    refresh = serializers.CharField(
        help_text=f"Refresh token will be used to generate new \
access token every {settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']} minutes ")
    access = serializers.CharField(
        help_text='Used in headers to authenticate users')


class TokenGenerateSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class TokenGenerateSerializerEmail(serializers.Serializer):
    email = serializers.EmailField(
        help_text='Email of user to verify and return tokens for')


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password])
    username = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('password', 'email', 'username')

    def create(self, validated_data):
        email = validated_data.get('email')
        password = validated_data.get('password')
        username = validated_data.get('username')
        user = User.objects\
            .create_user(email=email, password=password, username=username)
        return user


class ValidateOtpSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True)

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError('User does not exist')
        return user

    def validate(self, attrs):
        otp = attrs['otp']
        user: User = attrs['email']

        if not user.validate_otp(otp):
            raise serializers.ValidationError('Invalid OTP')

        return attrs


class ValidateRegistrationOtpSerializer(ValidateOtpSerializer):
    def save(self, **kwargs):
        user: User = self.validated_data['email']
        user.verified_email = True
        user.save()


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        # Get required info for validation
        email = attrs['email']
        password = attrs['password']

        """
        Check that the email is available in the User table
        """
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"email": 'Please provide a valid email and password'})

        if not user.check_password(password):
            raise serializers.ValidationError(
                {"email": 'Please provide a valid email and password'})

        return attrs


class ProfileSerializer(serializers.ModelSerializer):
    fullname = serializers.CharField(read_only=True)

    class Meta:
        model = Profile
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'profile'
        )

    def validate_phoneno(self, value):
        if value:
            # Check if this phone has been used by anyone
            qset = User.objects.filter(phone=value)

            if self.instance:
                qset = qset.exclude(pk=self.instance.pk)

            exists = qset.exists()
            if exists:
                raise serializers.ValidationError(
                    'This phone number has already been used')

        return value


class ForgetPasswordSerializer(serializers.Serializer):
    uidb64 = serializers.CharField(required=True)
    token = serializers.CharField(required=True)
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password])

    def validate(self, attrs):
        # Validate the uidb64 and token
        return attrs

    def save(self, **kwargs):
        # Get the user
        user: User = self.validated_data['user']
        password = self.validated_data['password']

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
                raise serializers.ValidationError(
                    'Please verify your email first')
        except User.DoesNotExist:
            raise serializers.ValidationError('User does not exist')
        return value


class ChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password])
    instance: AbstractBaseUser = None

    class Meta:
        model = User
        fields = (
            'id', 'email', 'old_password',
            'new_password',)
        extra_kwargs = {
            'email': {'read_only': True},
        }

    def validate(self, attrs):
        if not self.instance.check_password(attrs['old_password']):
            raise serializers.ValidationError(
                {'old_password': 'Old password is not correct'})
        return attrs

    def update(self, instance, validated_data):
        # Set password
        new_password = validated_data.get('new_password')
        instance.set_password(new_password)
        instance.save()

        return instance


class LoginResponseSerializer200(serializers.Serializer):
    user = UserSerializer()
    tokens = JWTTokenResponseSerializer()
