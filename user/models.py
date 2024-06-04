from urllib import request
from django.contrib.auth.password_validation import validate_password
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from rest_framework import status
from .permissions import *

class UserManager(BaseUserManager):
    def create_user(self, email, name, tc, password=None, password2=None, **extra_fields):
        print(name, password, password2)
        if not email:
            raise ValueError('The Email field must be set')
        if not email:
            raise ValueError("Users must have an email address")

        if password != password2:
            raise ValueError("Passwords don't match")

        """validate_password(password)

        if password is not validate_password(password):
            raise ValueError("One Captial , one numeric , one special, min_lenght = 8 ")"""

        user = self.model(
            email=self.normalize_email(email),
            name=name,
            tc=tc,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, tc, password=None, **extra_fields):

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        user = self.create_user(email, name, tc, password, password2=password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(verbose_name="Email", max_length=300, unique=True,)
    name = models.CharField(verbose_name="Name", max_length=200)
    tc = models.BooleanField()
    is_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_edit = models.BooleanField(default=False)
    is_delete = models.BooleanField(default=False)
    is_post = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "tc"]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return self.is_admin

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

    @is_staff.setter
    def is_staff(self, value):
        self.is_admin = value

    @property
    def is_superuser(self):
        "Is the user a superuser?"
        return self.is_admin

    @is_superuser.setter
    def is_superuser(self, value):
        self.is_admin = value