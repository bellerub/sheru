from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.db import models
from .validators import validate_absolute_path

# Create your models here.


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

# Remove username, use email field as username
class User(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        if self.first_name and self.last_name:
            return self.last_name + ", " + self.first_name
        return self.email

class ContainerTemplate(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    owner = models.ForeignKey(User, related_name='container_templates', on_delete=models.CASCADE)
    friendly_name = models.CharField(max_length=30, blank=True)
    image = models.CharField(max_length=256)
    shell = models.CharField(max_length=256)

    # Network Options
    network_disable = models.BooleanField(default=False)
    dns_server_1 = models.GenericIPAddressField(protocol='IPv4', null=True)
    dns_server_2 = models.GenericIPAddressField(protocol='IPv4', null=True)
    dns_search_domain = models.CharField(max_length=252, blank=True)

    # Advanced Options
    user_id = models.IntegerField(blank=True, null=True)
    working_dir = models.CharField(max_length=256, validators=[validate_absolute_path], default="/sheru")
    mount_volume = models.BooleanField(default=False)
    mount_location = models.CharField(max_length=256, validators=[validate_absolute_path], default="/sheru")

    def __str__(self):
        return self.image + ": " + self.shell

class UserDefaultTemplate(models.Model):
    user = models.OneToOneField(User, related_name='default_template', on_delete=models.CASCADE, primary_key=True)
    template = models.ForeignKey(ContainerTemplate, related_name='+', on_delete=models.CASCADE)

    def __str__(self):
        return self.template