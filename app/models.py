from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.db import models
from django.utils import timezone

class UserCreation(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    role = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    # Добавляем last_login только на уровне Django
    last_login = None  # Отключаем поле last_login из AbstractBaseUser

    objects = UserCreation()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'role']

    class Meta:
        db_table = 'users'
        managed = False

class Project(models.Model):
    manager = models.ForeignKey(User, on_delete=models.CASCADE, db_column='manager_id')
    project_name = models.CharField(max_length=255)
    project_description = models.TextField(null=True)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'projects'
        managed = False

class Task(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, db_column='project_id')
    worker = models.ForeignKey(
        User, 
        null=True, 
        on_delete=models.SET_NULL, 
        db_column='worker_id'
    )
    task_name = models.CharField(max_length=255)
    task_description = models.TextField(null=True)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tasks'
        managed = False

class ProjectMember(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, db_column='project_id')
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')

    class Meta:
        db_table = 'project_members'
        managed = False
        unique_together = ['project', 'user']