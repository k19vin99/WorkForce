from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.utils import timezone

class Empresa(models.Model):
    nombre = models.CharField(max_length=255)
    razon_social = models.CharField(max_length=255)
    rut = models.CharField(max_length=12)
    giro = models.CharField(max_length=255)
    cantidad_personal = models.IntegerField()
    direccion = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre

class Area(models.Model):
    nombre = models.CharField(max_length=255)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='areas')

    def __str__(self):
        return f"{self.nombre} - {self.empresa.nombre}"
    
class CustomUser(AbstractUser):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, null=True, blank=True)
    area = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True, blank=True)
    cargo = models.CharField(max_length=255, blank=True, null=True)
    fecha_contratacion = models.DateField(blank=True, null=True)
    foto_perfil = models.ImageField(upload_to='fotos_perfil/', null=True, blank=True)
    telefono = models.CharField(max_length=15, null=True, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    salud = models.CharField(max_length=30, choices=[
        ('fonasa', 'Fonasa'),
        ('banmedica', 'Banmédica'),
        ('colmena', 'Colmena Golden Cross'),
        ('consalud', 'Consalud'),
        ('cruzblanca', 'CruzBlanca'),
        ('esencial', 'Esencial'),
        ('masvida', 'Nueva Masvida'),
        ('vidatres', 'Vida Tres'),
    ], blank=True, null=True)
    afp = models.CharField(max_length=30, choices=[
        ('capital', 'AFP Capital'),
        ('cuprum', 'AFP Cuprum'),
        ('habitat', 'AFP Habitat'),
        ('modelo', 'AFP Modelo'),
        ('planvital', 'AFP Planvital'),
        ('provida', 'AFP Provida'),
        ('uno', 'AFP Uno'),
    ], blank=True, null=True)
    horario_asignado = models.CharField(max_length=20, choices=[
        ('8:00-17:30', '8:00 a 17:30'),
        ('9:00-18:30', '9:00 a 18:30'),
        ('21:00-8:00', '21:00 a 8:00'),
        ('otro', 'Otro'),
    ], null=True, blank=True)
    rut = models.CharField(max_length=12, unique=True, null=True, blank=True)

    def __str__(self):
        return self.username

class Liquidacion(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    sueldo_base = models.DecimalField(max_digits=10, decimal_places=2)
    gratificacion = models.DecimalField(max_digits=10, decimal_places=2)
    colacion = models.DecimalField(max_digits=10, decimal_places=2)
    movilizacion = models.DecimalField(max_digits=10, decimal_places=2)
    afp = models.DecimalField(max_digits=10, decimal_places=2)
    salud = models.DecimalField(max_digits=10, decimal_places=2)
    seguro_mutual = models.DecimalField(max_digits=10, decimal_places=2)
    sueldo_liquido = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    fecha = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        haberes = self.sueldo_base + self.gratificacion + self.colacion + self.movilizacion
        descuentos = self.afp + self.salud + self.seguro_mutual
        self.sueldo_liquido = haberes - descuentos
        super(Liquidacion, self).save(*args, **kwargs)

    def __str__(self):
        return f"Liquidación de {self.usuario.username} - {self.fecha}"


class CargaFamiliar(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    rut = models.CharField(max_length=12)
    parentesco = models.CharField(max_length=50, choices=[
        ('hijo/a', 'Hijo/a'),
        ('esposo/a', 'Esposo/a'),
        ('padre/madre', 'Padre/Madre'),
        ('conviviente', 'Conviviente'),
        ('otro', 'Otro'),
    ])
    fecha_nacimiento = models.DateField(null=True, blank=True)
    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='cargas_familiares')

    def __str__(self):
        return f'{self.nombre} {self.apellido} ({self.parentesco})'

class Asistencia(models.Model):
    colaborador = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    fecha = models.DateField(auto_now_add=True)
    hora_entrada = models.TimeField(null=True, blank=True)
    hora_salida = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.colaborador} - {self.fecha}"
    
class Solicitud(models.Model):
    TIPOS_SOLICITUD = [
        ('vacaciones', 'Días de Vacaciones'),
        ('tramite', 'Permiso Trámite Personal'),
        ('administrativo', 'Día Administrativo'),
        ('cumpleanos', 'Descanso por Cumpleaños'),
        ('cumpleanos_hijo', 'Descanso por Cumpleaños Hijo/a'),
        ('otra', 'Otra'),
    ]

    ESTADO_SOLICITUD = [
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
    ]

    colaborador = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=50, choices=TIPOS_SOLICITUD)
    descripcion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateField(auto_now_add=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    estado = models.CharField(max_length=50, choices=ESTADO_SOLICITUD, default='pendiente')

    @property
    def dias_vacaciones(self):
        if self.tipo == 'vacaciones':
            antiguedad_meses = (date.today().year - self.colaborador.date_joined.year) * 12 + date.today().month - self.colaborador.date_joined.month
            return antiguedad_meses * 1.8
        return 0

    def __str__(self):
        return f"{self.colaborador.username} - {self.tipo}"

User = get_user_model()

class Curso(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    supervisor = models.ForeignKey(User, on_delete=models.CASCADE)
    participantes = models.ManyToManyField(User, related_name='cursos')

    def __str__(self):
        return self.nombre

class Modulo(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name="modulos")
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField()
    archivo = models.FileField(upload_to='modulos_archivos/', null=True, blank=True)

    def __str__(self):
        return self.titulo

class Comentario(models.Model):
    modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE, related_name="comentarios")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    comentario = models.TextField()
    fecha = models.DateTimeField(default=timezone.now)  # Asegúrate de que timezone.now esté como default

    def __str__(self):
        return f"Comentario de {self.usuario.username} en {self.modulo.titulo}"
    
class Beneficio(models.Model):
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField()
    imagen = models.ImageField(upload_to='beneficios/', null=True, blank=True)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.titulo
    
class Denuncia(models.Model):
    ESTADOS_DENUNCIA = [
        ('pendiente', 'Pendiente'),
        ('revision', 'En Revisión'),
        ('resuelta', 'Resuelta'),
    ]
    denunciado = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='denuncias_recibidas')
    denunciante = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='denuncias_realizadas')
    motivo = models.CharField(max_length=255)
    descripcion = models.TextField()
    evidencias = models.FileField(upload_to='evidencias_denuncias/', null=True, blank=True)
    contacto_urgencia = models.CharField(max_length=100)
    estado = models.CharField(max_length=50, choices=ESTADOS_DENUNCIA, default='pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_limite = models.DateField(null=True, blank=True)

    PRIORIDADES_DENUNCIA = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
    ]

    prioridad = models.CharField(max_length=50, choices=PRIORIDADES_DENUNCIA, default='media')

    def __str__(self):
        return f"Denuncia de {self.denunciante} contra {self.denunciado}"
    
class NotaDenuncia(models.Model):
    denuncia = models.ForeignKey(Denuncia, on_delete=models.CASCADE, related_name='notas')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    nota = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Nota de {self.usuario.username} - {self.denuncia.id}"
    
class HistorialDenuncia(models.Model):
    denuncia = models.ForeignKey(Denuncia, on_delete=models.CASCADE, related_name='historial')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    accion = models.CharField(max_length=255)  # Ej: "Estado actualizado a resuelta"
    fecha = models.DateTimeField(auto_now_add=True)

class EvidenciaDenuncia(models.Model):
    denuncia = models.ForeignKey(Denuncia, on_delete=models.CASCADE, related_name='evidencia_set')
    archivo = models.FileField(upload_to='evidencias_denuncias/')

class Publicacion(models.Model):
    titulo = models.CharField(max_length=255)
    contenido = models.TextField()
    imagen = models.ImageField(upload_to='publicaciones/', null=True, blank=True)  # Campo para la imagen
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    autor = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.titulo