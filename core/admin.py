from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        ('Perfil', {'fields': (
            'user_type', 'categoria', 'ajuda_custo_classe', 'cadastro_completo', 'is_approved'
        )}),
    )


admin.site.register(CustomUser, CustomUserAdmin)

