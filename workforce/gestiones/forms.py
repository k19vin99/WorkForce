from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import Group
from .models import Liquidacion, CargaFamiliar, CustomUser, Solicitud, Curso, Modulo, Comentario, Beneficio, Area, Denuncia, NotaDenuncia, EvidenciaDenuncia, Publicacion
from django.contrib.auth import get_user_model
from django.forms import modelformset_factory

class CustomUserCreationForm(UserCreationForm):
    grupo = forms.ModelChoiceField(queryset=Group.objects.all(), required=True, label="Grupo")
    first_name = forms.CharField(max_length=30, required=True, label="Nombre")
    last_name = forms.CharField(max_length=30, required=True, label="Apellido")
    fecha_contratacion = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), 
        required=True, 
        label="Fecha de contratación"
    )
    telefono = forms.CharField(max_length=15, required=True, label="Número de Teléfono")
    fecha_nacimiento = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), 
        required=True, 
        label="Fecha de Nacimiento"
    )
    direccion = forms.CharField(max_length=255, required=True, label="Dirección")
    salud = forms.ChoiceField(choices=[
        ('fonasa', 'Fonasa'),
        ('banmedica', 'Banmédica'),
        ('colmena', 'Colmena Golden Cross'),
        ('consalud', 'Consalud'),
        ('cruzblanca', 'CruzBlanca'),
        ('esencial', 'Esencial'),
        ('masvida', 'Nueva Masvida'),
        ('vidatres', 'Vida Tres'),
    ], required=True, label="Plan de Salud")
    afp = forms.ChoiceField(choices=[
        ('capital', 'AFP Capital'),
        ('cuprum', 'AFP Cuprum'),
        ('habitat', 'AFP Habitat'),
        ('modelo', 'AFP Modelo'),
        ('planvital', 'AFP Planvital'),
        ('provida', 'AFP Provida'),
        ('uno', 'AFP Uno'),
    ], required=True, label="AFP")
    horario_asignado = forms.ChoiceField(choices=[
        ('8:00-17:30', '8:00 a 17:30'),
        ('9:00-18:30', '9:00 a 18:30'),
        ('21:00-8:00', '21:00 a 8:00'),
        ('otro', 'Otro'),
    ], required=True, label="Horario Asignado")

    class Meta:
        model = CustomUser
        fields = [
            'username', 'first_name', 'last_name', 'rut', 'cargo', 
            'telefono', 'fecha_nacimiento', 'direccion', 'salud', 'afp', 'horario_asignado', 
            'fecha_contratacion', 'grupo', 'password1', 'password2'
        ]

    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        if CustomUser.objects.filter(rut=rut).exists():
            raise forms.ValidationError("El RUT ya está registrado.")
        return rut


class LiquidacionSueldoForm(forms.ModelForm):
    class Meta:
        model = Liquidacion
        fields = ['usuario', 'sueldo_base', 'gratificacion', 'colacion', 'movilizacion', 'afp', 'salud', 'seguro_mutual']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(LiquidacionSueldoForm, self).__init__(*args, **kwargs)
        if user and user.empresa:
            self.fields['usuario'].queryset = CustomUser.objects.filter(empresa=user.empresa)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Obtiene el usuario desde kwargs
        super(LiquidacionSueldoForm, self).__init__(*args, **kwargs)
        if user and user.empresa:  # Verifica que el usuario y su empresa existan
            self.fields['usuario'].queryset = CustomUser.objects.filter(empresa=user.empresa)

class EditarUsuarioForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'cargo', 'telefono', 'fecha_nacimiento', 'area']  # Añadir 'area'

    # Definir un campo ModelChoiceField para mostrar las áreas disponibles como un dropdown
    area = forms.ModelChoiceField(queryset=Area.objects.none(), required=False)

    def __init__(self, *args, **kwargs):
        super(EditarUsuarioForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.empresa:
            # Filtrar las áreas por la empresa del colaborador
            self.fields['area'].queryset = Area.objects.filter(empresa=self.instance.empresa)

class CargaFamiliarForm(forms.ModelForm):
    fecha_nacimiento = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date', 
            'class': 'form-control',  # Clase Bootstrap
            'style': 'max-width: 300px;'  # Limitar el ancho del campo
        }),
        label="Fecha de nacimiento",
        required=True
    )

    class Meta:
        model = CargaFamiliar
        fields = ['usuario', 'nombre', 'apellido', 'rut', 'parentesco', 'fecha_nacimiento']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(CargaFamiliarForm, self).__init__(*args, **kwargs)
        if user and user.empresa:
            self.fields['usuario'].queryset = CustomUser.objects.filter(empresa=user.empresa)


class SolicitudForm(forms.ModelForm):
    class Meta:
        model = Solicitud
        fields = ['tipo', 'descripcion', 'fecha_inicio', 'fecha_fin']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
        }

class ContactForm(forms.Form):
    MOTIVO_CONTACTO_CHOICES = [
        ('', 'Selecciona'),
        ('evaluar', 'Me interesa WorkForce para mi empresa'),
        ('soporte', 'Soy supervisor y necesito soporte'),
        ('oportunidades', 'Estoy buscando oportunidades laborales'),
    ]

    motivo_contacto = forms.ChoiceField(choices=MOTIVO_CONTACTO_CHOICES, required=True, label='¿Motivo de Contacto?')
    nombre = forms.CharField(max_length=100, required=True, label='Nombre')
    apellido = forms.CharField(max_length=100, required=True, label='Apellido')
    numero_telefono = forms.CharField(max_length=15, required=True, label='Número de teléfono')
    correo = forms.EmailField(required=True, label='Correo')
    nombre_empresa = forms.CharField(max_length=100, required=True, label='Nombre de la empresa')
    cantidad_colaboradores = forms.ChoiceField(choices=[('', 'Elije'), ('1-20', '1-20'), ('21-70', '21-70'), ('71-100', '71-100'), ('101+', '101+')], required=True, label='Cantidad de colaboradores')
    cargo = forms.CharField(max_length=100, required=True, label='Cargo')
    area_desempeno = forms.CharField(max_length=100, required=True, label='Área de desempeño')
    rubro = forms.CharField(max_length=100, required=True, label='Rubro')
    mensaje = forms.CharField(widget=forms.Textarea, required=False, label='¿En qué podemos ayudarte?')

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email']

class EditProfilePhotoForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['foto_perfil']

class CustomPasswordChangeForm(PasswordChangeForm):
    class Meta:
        model = CustomUser
        fields = ['old_password', 'new_password1', 'new_password2']
        widgets = {
            'old_password': forms.PasswordInput(attrs={'class': 'form-control'}),
            'new_password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'new_password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

class CursoForm(forms.ModelForm):
    participantes = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Participantes"
    )

    class Meta:
        model = Curso
        fields = ['nombre', 'descripcion', 'participantes']

    def __init__(self, *args, **kwargs):
        supervisor = kwargs.pop('supervisor', None)
        super(CursoForm, self).__init__(*args, **kwargs)
        if supervisor:
            # Filtra los participantes para que solo sean los colaboradores de la empresa del supervisor
            self.fields['participantes'].queryset = CustomUser.objects.filter(empresa=supervisor.empresa)


class ModuloForm(forms.ModelForm):
    class Meta:
        model = Modulo
        fields = ['titulo', 'descripcion', 'archivo']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
            'archivo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['comentario']


class EditarParticipantesForm(forms.ModelForm):
    participantes = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Participantes"
    )

    class Meta:
        model = Curso
        fields = ['participantes']

class BeneficioForm(forms.ModelForm):
    class Meta:
        model = Beneficio
        fields = ['titulo', 'descripcion', 'imagen']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class DenunciaForm(forms.ModelForm):
    class Meta:
        model = Denuncia
        fields = ['denunciado', 'motivo', 'descripcion', 'contacto_urgencia']  # Quitamos 'evidencias'
        labels = {
            'denunciado': 'Quiero denunciar a',
            'motivo': 'Motivo',
            'descripcion': 'Descripción',
            'contacto_urgencia': 'Datos de contacto para urgencias'
        }
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4}),
        }


class NotaDenunciaForm(forms.ModelForm):
    class Meta:
        model = NotaDenuncia
        fields = ['nota']
        labels = {
            'nota': 'Agregar Nota',
        }
        widgets = {
            'nota': forms.Textarea(attrs={'rows': 10}),
        }

class EvidenciaDenunciaForm(forms.ModelForm):
    class Meta:
        model = EvidenciaDenuncia
        fields = ['archivo']
        labels = {
            'archivo': 'Evidencia',
        }

# Usamos modelformset para manejar múltiples archivos de evidencia
EvidenciaFormset = modelformset_factory(EvidenciaDenuncia, form=EvidenciaDenunciaForm, extra=3)

class PublicacionForm(forms.ModelForm):
    class Meta:
        model = Publicacion
        fields = ['titulo', 'contenido', 'imagen']  # Incluye el campo de imagen
        labels = {
            'titulo': 'Título',
            'contenido': 'Descripción',
            'imagen': 'Imagen',
        }
        widgets = {
            'contenido': forms.Textarea(attrs={'rows': 4}),
        }