
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models, transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from Curriculum.models import Curriculum, CurriculumEnrollment

from utils.base.general import random_otp, send_email
from utils.base.validators import validate_special_char
from django.core.cache import cache
from django.conf import settings


class UserManager(BaseUserManager):
    def create_base_user(
            self, email, username, is_active=True,
            is_staff=False, is_admin=False
    ) -> AbstractBaseUser:
        if not email:
            raise ValueError("User must provide an email")

        user: User = self.model(
            email=self.normalize_email(email),
            username=username,
        )
        user.active = is_active
        user.admin = is_admin
        user.staff = is_staff
        user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_user(
            self, email, username, password=None, is_active=True,
            is_staff=False, is_admin=False
    ):
        if not password:
            raise ValueError("User must provide a password")
        user = self.create_base_user(
            email, username, is_active, is_staff, is_admin)
        user.set_password(password)
        user.save()
        return user

    def create_staff(self, email, username, password=None):
        user = self.create_user(
            email, username, password, is_staff=True)
        return user

    def create_superuser(self, email, username, password=None):
        user = self.create_user(
            email, username, password, is_staff=True, is_admin=True)
        return user

    def get_staffs(self):
        return self.filter(staff=True)


class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    username = models.CharField(
        max_length=60, unique=True,
        validators=[validate_special_char],
        help_text="Username must be unique and \
must not contain special characters"
    )
    active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    verified_email = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    REQUIRED_FIELDS = ["username"]
    USERNAME_FIELD = "email"

    objects = UserManager()

    def has_perm(self, perm, obj=None):  # pragma: no cover
        return True

    def has_module_perms(self, app_label):  # pragma: no cover
        return True

    def __str__(self) -> str:
        return self.username

    def set_otp(self):
        otp = random_otp()
        cache.set(f"otp_{self.pk}", otp, timeout=settings.OTP_CACHE_TIMEOUT)
        return otp

    def validate_otp(self, otp):
        valid = cache.get(f"otp_{self.pk}") == otp
        if settings.DEBUG:
            if otp == settings.DEFAULT_OTP:
                valid = True
        if valid:
            cache.delete(f"otp_{self.pk}")
        return valid

    def email_user(self, subject, message):
        val = send_email(subject=subject, message=message, email=self.email)
        return True if val else False

    def get_curriculum_enrollments(self):
        """
        Get the curriculums this user
        is enrolled.
        """
        return self.curriculumenrollment_set.all()

    def get_curriculum_enrollment(self, curriculum):
        return self.get_curriculum_enrollments()\
            .get(curriculum=curriculum)

    def has_enrolled_curriculum(self, curriculum):
        try:
            self.get_curriculum_enrollment(curriculum)
        except CurriculumEnrollment.DoesNotExist:
            return False
        return True

    @transaction.atomic
    def enroll_curriculum(self, curriculum: Curriculum):
        enrollment = self.curriculumenrollment_set.create(
            curriculum=curriculum,
        )

        for syllabi in curriculum.syllabus:
            for topic in syllabi.get_topics():
                enrollment.syllabiprogress_set.create(
                    syllabi=syllabi,
                    topic=topic
                )

        return enrollment

    @property
    def is_active(self) -> bool:
        return self.active

    @property
    def is_staff(self) -> bool:
        return self.staff

    @property
    def is_admin(self) -> bool:
        return self.admin

    @property
    def is_personnel(self) -> bool:
        return self.staff or self.admin


class Skill(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self) -> str:
        return self.name.title()


class Interest(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self) -> str:
        return self.name.title()


class Personality(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self) -> str:
        return self.name.title()


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fullname = models.CharField(
        max_length=30,
        validators=[validate_special_char],
        blank=True)
    bio = models.TextField(max_length=1000, blank=True)
    github = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    skills = models.ManyToManyField(Skill, blank=True)
    interest = models.ManyToManyField(Interest, blank=True)
    personality = models.ForeignKey(
        Personality, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self) -> str:
        return self.get_fullname

    @property
    def get_fullname(self) -> str:
        return self.fullname.title()


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


class UsedResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.user.email

    class Meta:
        verbose_name_plural = "Used Reset Tokens"
