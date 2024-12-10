from django import forms
import re
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import Group
from .models import CargaFamiliar, CustomUser, Solicitud, Curso, Beneficio, Area, Denuncia, NotaDenuncia, EvidenciaDenuncia, Publicacion, DocumentoEmpresa, SolicitudVacaciones, ProgresoParticipante
from django.contrib.auth import get_user_model
from django.forms import modelformset_factory
import datetime
from django.core.exceptions import ValidationError
from .models import CustomUser as User


#Formulario de Registro de Usuario
class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        max_length=150,
        required=True,
        label="Nombre de Usuario",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    grupo = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        required=True,
        label="Grupo",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    genero = forms.ChoiceField(
        choices=CustomUser.GENERO_CHOICES,
        required=True,
        label="Género",
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'  # Clase de Bootstrap para botones de radio estilizados
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        label="Primer Nombre",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        label="Primer Apellido",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    segundo_nombre = forms.CharField(
        max_length=30,
        required=False,
        label="Segundo Nombre",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    segundo_apellido = forms.CharField(
        max_length=30,
        required=False,
        label="Segundo Apellido",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        required=True,
        label="Correo Electrónico",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    rut = forms.CharField(
        max_length=12,
        required=True,
        label="RUT",
        widget=forms.TextInput(attrs={
            'placeholder': 'Ej: 12345678-9',
            'class': 'form-control'
        })
    )
    area = forms.ModelChoiceField(
        queryset=Area.objects.all(),
        required=True,
        label="Área",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    fecha_contratacion = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=True,
        label="Fecha de Contratación"
    )
    telefono = forms.CharField(
        max_length=9,
        required=True,
        label="Número de Teléfono",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: 912345678'
        })
    )
    fecha_nacimiento = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=True,
        label="Fecha de Nacimiento"
    )
    direccion = forms.CharField(
        max_length=255,
        required=True,
        label="Dirección",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    salud = forms.ChoiceField(
        choices=[
            ('fonasa', 'Fonasa'),
            ('banmedica', 'Banmédica'),
            ('colmena', 'Colmena Golden Cross'),
            ('consalud', 'Consalud'),
            ('cruzblanca', 'CruzBlanca'),
            ('esencial', 'Esencial'),
            ('masvida', 'Nueva Masvida'),
            ('vidatres', 'Vida Tres'),
        ],
        required=True,
        label="Plan de Salud",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    certificado_salud = forms.FileField(
        required=True,
        label="Certificado de Salud (PDF)",
        widget=forms.ClearableFileInput(attrs={'accept': '.pdf', 'class': 'form-control'})
    )
    afp = forms.ChoiceField(
        choices=[
            ('capital', 'AFP Capital'),
            ('cuprum', 'AFP Cuprum'),
            ('habitat', 'AFP Habitat'),
            ('modelo', 'AFP Modelo'),
            ('planvital', 'AFP Planvital'),
            ('provida', 'AFP Provida'),
            ('uno', 'AFP Uno'),
        ],
        required=True,
        label="AFP",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    certificado_afp = forms.FileField(
        required=True,
        label="Certificado AFP (PDF)",
        widget=forms.ClearableFileInput(attrs={'accept': '.pdf', 'class': 'form-control'})
    )
    horario_asignado = forms.ChoiceField(
        choices=[
            ('8:00-17:30', '8:00 a 17:30'),
            ('9:00-18:30', '9:00 a 18:30'),
            ('21:00-8:00', '21:00 a 8:00'),
            ('otro', 'Otro'),
        ],
        required=True,
        label="Horario Asignado",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    cargo = forms.CharField(
        max_length=255,
        required=True,
        label="Cargo",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}),
    )
    password2 = forms.CharField(
        label="Confirmar Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmar Contraseña'}),
    )
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Extraer el usuario si se pasa al formulario
        super().__init__(*args, **kwargs)  # Llamar al constructor base
        # Filtrar las áreas según la empresa del usuario que registra
        if user and user.empresa:
            self.fields['area'].queryset = Area.objects.filter(empresa=user.empresa)
        else:
            self.fields['area'].queryset = Area.objects.none()
    class Meta:
        model = CustomUser
        fields = [
            'username', 'first_name', 'segundo_nombre', 'last_name', 'segundo_apellido', 'email', 'rut', 'area', 'cargo',
            'telefono', 'fecha_nacimiento', 'direccion', 'salud', 'afp', 'horario_asignado',
            'fecha_contratacion', 'grupo', 'password1', 'password2', 'genero', 'certificado_afp', 'certificado_salud'
        ]

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if not telefono.isdigit():
            raise forms.ValidationError("El número de teléfono debe contener solo dígitos.")
        if not telefono.startswith('9'):
            raise forms.ValidationError("El número de teléfono debe comenzar con un '9'.")
        if len(telefono) != 9:
            raise forms.ValidationError("El número de teléfono debe tener exactamente 9 dígitos.")
        return telefono

    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        # Verificar formato correcto (Ej: 12345678-9)
        rut_pattern = r'^\d{1,8}-[\dkK]$'
        if not re.match(rut_pattern, rut):
            raise forms.ValidationError("El formato del RUT no es válido. Debe ser en formato 12345678-9.")
        return rut

class CustomUserChangeForm(forms.ModelForm):
    grupo = forms.ModelMultipleChoiceField(
    queryset=Group.objects.all(),
    required=False,
    label="Grupo",
    widget=forms.CheckboxSelectMultiple(attrs={
        'class': 'form-check-input'
    }))
    certificado_afp = forms.FileField(
        required=False,
        label="Certificado AFP",
        widget=forms.ClearableFileInput(attrs={
            'accept': '.pdf',
            'class': 'form-control'
        }),
    )
    certificado_salud = forms.FileField(
        required=False,
        label="Certificado Salud",
        widget=forms.ClearableFileInput(attrs={
            'accept': '.pdf',
            'class': 'form-control'
        }),
    )
    area = forms.ModelChoiceField(
        queryset=Area.objects.all(),
        required=True,
        label="Área",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    fecha_nacimiento = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        required=False,
        label="Fecha de Nacimiento"
    )
    fecha_contratacion = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        required=False,
        label="Fecha de Contratación"
    )
    rut = forms.CharField(
        max_length=12,
        required=True,
        label="RUT",
        widget=forms.TextInput(attrs={
            'placeholder': 'Ej: 12345678-9',
            'class': 'form-control'
        })
    )
    username = forms.CharField(
        max_length=150,
        required=True,
        label="Nombre de Usuario",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        label="Primer Nombre",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    segundo_nombre = forms.CharField(
        max_length=30,
        required=False,
        label="Segundo Nombre",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        label="Primer Apellido",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    segundo_apellido = forms.CharField(
        max_length=30,
        required=False,
        label="Segundo Apellido",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        required=True,
        label="Correo Electrónico",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    telefono = forms.CharField(
        max_length=9,
        required=True,
        label="Número de Teléfono",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: 912345678'
        })
    )
    direccion = forms.CharField(
        max_length=255,
        required=True,
        label="Dirección",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    cargo = forms.CharField(
        max_length=255,
        required=True,
        label="Cargo",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    salud = forms.ChoiceField(
        choices=[
            ('fonasa', 'Fonasa'),
            ('banmedica', 'Banmédica'),
            ('colmena', 'Colmena Golden Cross'),
            ('consalud', 'Consalud'),
            ('cruzblanca', 'CruzBlanca'),
            ('esencial', 'Esencial'),
            ('masvida', 'Nueva Masvida'),
            ('vidatres', 'Vida Tres'),
        ],
        required=True,
        label="Plan de Salud",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    afp = forms.ChoiceField(
        choices=[
            ('capital', 'AFP Capital'),
            ('cuprum', 'AFP Cuprum'),
            ('habitat', 'AFP Habitat'),
            ('modelo', 'AFP Modelo'),
            ('planvital', 'AFP Planvital'),
            ('provida', 'AFP Provida'),
            ('uno', 'AFP Uno'),
        ],
        required=True,
        label="AFP",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    horario_asignado = forms.ChoiceField(
        choices=[
            ('8:00-17:30', '8:00 a 17:30'),
            ('9:00-18:30', '9:00 a 18:30'),
            ('21:00-8:00', '21:00 a 8:00'),
            ('otro', 'Otro'),
        ],
        required=True,
        label="Horario Asignado",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = CustomUser
        fields = [
            'username', 'first_name', 'segundo_nombre', 'last_name', 'segundo_apellido', 'email', 'rut', 'area', 'cargo',
            'telefono', 'fecha_nacimiento', 'direccion', 'salud', 'afp', 'horario_asignado',
            'fecha_contratacion', 'grupo', 'certificado_afp', 'certificado_salud'
        ]

    def __init__(self, *args, **kwargs):
        super(CustomUserChangeForm, self).__init__(*args, **kwargs)
        # Si el usuario tiene grupos asociados, seleccionarlos por defecto
        if self.instance.pk:
            self.fields['grupo'].initial = self.instance.groups.all()



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
    tipo_certificado = forms.ChoiceField(
        choices=CargaFamiliar.TIPO_CERTIFICADO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Tipo de Certificado",
        required=True
    )
    archivo = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
        label="Archivo del Certificado",
        required=True  # El archivo puede no ser obligatorio
    )

    class Meta:
        model = CargaFamiliar
        fields = ['usuario', 'nombre', 'apellido', 'rut', 'parentesco', 'fecha_nacimiento', 'tipo_certificado', 'archivo']

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
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
            'fecha_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

class SolicitudVacacionesForm(forms.ModelForm):
    class Meta:
        model = SolicitudVacaciones
        fields = ['fecha_inicio', 'fecha_fin', 'motivo']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')

        # Validar que la fecha de inicio no sea posterior a la fecha de fin
        if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:
            raise forms.ValidationError("La fecha de inicio no puede ser posterior a la fecha de fin.")

        # Verificar solapamientos con solicitudes aprobadas
        solicitudes_aprobadas = SolicitudVacaciones.objects.filter(
            colaborador=self.user,
            estado='aprobada',
            fecha_inicio__lte=fecha_fin,
            fecha_fin__gte=fecha_inicio
        )
        if solicitudes_aprobadas.exists():
            raise forms.ValidationError("Las fechas seleccionadas ya están reservadas. Por favor, elija otra fecha.")

        return cleaned_data

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


class EditProfilePhotoForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['foto_perfil']

class CustomPasswordChangeForm(PasswordChangeForm):
    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1')

        # Verificar longitud mínima
        if len(password) < 8:
            raise ValidationError("La contraseña debe tener al menos 8 caracteres.")

        # Verificar al menos un carácter en mayúscula
        if not any(char.isupper() for char in password):
            raise ValidationError("La contraseña debe contener al menos una letra mayúscula.")

        # Verificar al menos un número
        if not any(char.isdigit() for char in password):
            raise ValidationError("La contraseña debe contener al menos un número.")

        # Verificar al menos un símbolo
        if not any(char in "!@#$%^&*()-_+=<>?/.,:;" for char in password):
            raise ValidationError("La contraseña debe contener al menos un símbolo especial (!@#$%^&*()-_+=<>?/.,:;).")

        return password

class CursoForm(forms.ModelForm):

    class Meta:
        model = Curso
        fields = ['nombre', 'descripcion']

    def __init__(self, *args, **kwargs):
        supervisor = kwargs.pop('supervisor', None)
        super(CursoForm, self).__init__(*args, **kwargs)
        if supervisor:
            # Filtra los participantes para que solo sean los colaboradores de la empresa del supervisor
            self.fields['participantes'].queryset = CustomUser.objects.filter(empresa=supervisor.empresa)



class EditarParticipantesForm(forms.ModelForm):
    participantes = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),  # Puedes filtrar usuarios aquí si lo necesitas
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Participantes",
    )

    class Meta:
        model = Curso
        fields = ['participantes']  # Incluir solo el campo 'participantes'

class ActualizarProgresoForm(forms.ModelForm):
    progreso = forms.IntegerField(
        min_value=0, 
        max_value=100, 
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Porcentaje de progreso'})
    )

    class Meta:
        model = ProgresoParticipante
        fields = ['progreso']

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
        fields = ['denunciado', 'motivo', 'descripcion', 'contacto_urgencia']
        labels = {
            'denunciado': 'Quiero denunciar a',
            'motivo': 'Motivo',
            'descripcion': 'Descripción',
            'contacto_urgencia': 'Datos de contacto para urgencias'
        }
        widgets = {
            'denunciado': forms.Select(attrs={'class': 'form-control'}),
            'motivo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'contacto_urgencia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '9XXXXXXXX',
                'maxlength': '9'
            }),
        }

    def clean_contacto_urgencia(self):
        contacto = self.cleaned_data.get('contacto_urgencia')

        # Validar solo números
        if not contacto.isdigit():
            raise ValidationError("El contacto debe contener solo números.")

        # Validar que comience con 9
        if not contacto.startswith('9'):
            raise ValidationError("El contacto debe comenzar con un 9.")

        # Validar longitud exacta de 9 dígitos
        if len(contacto) != 9:
            raise ValidationError("El contacto debe tener exactamente 9 dígitos (Ejemplo: 9XXXXXXXX).")

        return contacto


class NotaDenunciaForm(forms.ModelForm):
    class Meta:
        model = NotaDenuncia
        fields = ['nota']
        labels = {
            'nota': '',  # Dejar vacío para no mostrar el label "Agregar Nota"
        }
        widgets = {
            'nota': forms.Textarea(attrs={
                'placeholder': 'Escribe aquí tu nota...', 
                'rows': 6,  # Puedes ajustar el número de filas según lo que necesites
                'class': 'form-control'  # Añadir la clase para estilos adicionales
            }),
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

class DocumentoEmpresaForm(forms.ModelForm):
    class Meta:
        model = DocumentoEmpresa
        fields = ['titulo', 'descripcion', 'archivo']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título del Documento'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Descripción'}),
            'archivo': forms.FileInput(attrs={'class': 'form-control'}),
        }