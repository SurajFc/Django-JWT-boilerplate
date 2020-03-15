
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        if email is None:
            raise TypeError("Users must have an email.")

        user = self.model(
            email=self.normalize_email(email), **kwargs)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self,  email, password, **kwargs):
        """
        Create and return a `User` with superuser (admin) permissions.
        """
        if not email:
            raise ValueError("Users must have an email")

        user = self.model(

            email=self.normalize_email(email),
            is_staff=True,
            is_confirmed=True,
            is_superuser=True,
            **kwargs
        )

        user.set_password(password)
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):

    user_id = models.CharField(
        primary_key=True, default=uuid.uuid4, unique=True, editable=False, max_length=250)
    fname = models.CharField(max_length=255)
    lname = models.CharField(max_length=255)
    mobile = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars', blank=True)
    email = models.EmailField(db_index=True, unique=True)
    is_confirmed = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['fname', 'lname']

    objects = UserManager()

    class Meta:
        db_table = 'user'


# contact us form
class ContactUs(models.Model):
    fname = models.CharField(max_length=200)
    lname = models.CharField(max_length=200)
    email = models.EmailField(max_length=200)
    text = models.TextField()

    class Meta:
        db_table = "contactus"
