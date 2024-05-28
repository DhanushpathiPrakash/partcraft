from urllib import request
from django.contrib.auth.password_validation import validate_password
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from rest_framework import status
from .permissions import *

class UserManager(BaseUserManager):
    def create_user(self, email, name, tc, password=None, password2=None):
        """
        Creates and saves a User with the given email, name, password and tc.
        """
        if not email:
            raise ValueError({"status": "error", "Message": "Users must have an email address"})

        if password != password2:
            raise ValueError({"status": "error", "Message": "Passwords must match"})

        validate_password(password)
        user = self.model(
            email=self.normalize_email(email),
            name=name,
            tc=tc,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, tc, password=None):
        """
        Creates and saves a superuser with the given email, name, password and tc.
        """
        user = self.create_user(
            email,
            password=password,
            name=name,
            tc=tc,
        )
        user.is_admin = True
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
