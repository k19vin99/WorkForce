from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Empresa, Area
from django.contrib.auth.models import Group

# Inline para las áreas
class AreaInline(admin.TabularInline):
    model = Area
    extra = 1  # Número de áreas adicionales vacías para añadir de forma inmediata
    fields = ['nombre']

# CustomUserAdmin para gestionar usuarios
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'is_staff', 'is_active', 'empresa', 'area','cargo', 'rut', 'fecha_contratacion', 'fecha_nacimiento')
    list_filter = ('is_staff', 'is_active', 'groups', 'empresa', 'area')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': (
            'first_name', 
            'last_name', 
            'email', 
            'empresa', 
            'area', 
            'cargo',
            'rut', 
            'telefono', 
            'fecha_nacimiento', 
            'fecha_contratacion', 
            'direccion', 
            'foto_perfil', 
            'salud', 
            'afp', 
            'horario_asignado',
            'genero'
        )}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 
                'email', 
                'password1', 
                'password2', 
                'is_staff', 
                'is_active', 
                'groups', 
                'empresa', 
                'area', 
                'rut', 
                'telefono', 
                'fecha_nacimiento', 
                'fecha_contratacion', 
                'direccion', 
                'foto_perfil', 
                'salud', 
                'afp', 
                'horario_asignado'
            )}
        ),
    )
    search_fields = ('username', 'email', 'rut')
    ordering = ('username',)

# Admin para las empresas
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'razon_social', 'rut', 'giro', 'cantidad_personal', 'direccion')
    search_fields = ('nombre', 'razon_social', 'rut')
    list_filter = ('giro',)
    inlines = [AreaInline]  # Agregamos el inline de áreas

# Admin para las áreas
class AreaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'empresa')
    list_filter = ('empresa',)
    search_fields = ('nombre', 'empresa__nombre')

admin.site.register(Empresa, EmpresaAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Area, AreaAdmin)

# Mantener el grupo de usuarios
admin.site.unregister(Group)
admin.site.register(Group)
