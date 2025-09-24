from django.contrib.auth.models import AbstractUser
from django.db import models

USER_TYPES = (
    ('admin', 'Admin'),
    ('gestor', 'Gestor'),
    ('monitor', 'Monitor'),
)

class CustomUser(AbstractUser):
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='monitor')
