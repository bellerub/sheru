from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

# Custom user for potential future attributes
class User(AbstractUser):


    def __str__(self):
        return self.username

class ContainerTemplate(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    owner = models.ForeignKey(User, related_name='container_templates', on_delete=models.CASCADE)
    image = models.CharField(max_length=256)
    shell = models.CharField(max_length=256)

    def __str__(self):
        return self.image + ": " + self.shell


class UserDefaultTemplate(models.Model):
    id = models.AutoField(primary_key=True)

    user = models.ForeignKey(User, related_name='default_template', on_delete=models.CASCADE)
    template = models.ForeignKey(ContainerTemplate, related_name='+', on_delete=models.CASCADE)

    def __str__(self):
        return self.template