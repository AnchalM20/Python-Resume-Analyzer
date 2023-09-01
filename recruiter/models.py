from django.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager

# Create your models here.
# class User(AbstractUser):
#     email = models.EmailField(unique=True,max_length=255)
#     USERNAME_FIELD = 'email'

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class registeredUser(AbstractUser):
    username = models.CharField(db_index=True, unique=True, max_length=255)
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']    

    objects = CustomUserManager()


