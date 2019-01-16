from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

import base64
import os

from myapp.settings import AUTH_USER_MODEL


# Create your models here.


class User(AbstractUser):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(blank=True, max_length=30)
    email = models.EmailField(blank=False, unique=True)
    password = models.CharField(blank=True, max_length=100)
    join_date = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'password')

    def __str__(self):
        return str(self.user_id)

class Employee(models.Model):
    address = models.TextField(blank=True)
    employee_name = models.TextField(blank=True)

    def __str__(self):
        return self.employee_name

class Organisation(models.Model):
    org_name = models.TextField(blank=True)
    org_owner = models.TextField(blank=True)
    org_type = models.TextField(blank=True)
    org_address = models.TextField(blank=True)

    def __str__(self):
        return self.org_name