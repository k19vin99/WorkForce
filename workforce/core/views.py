from django.shortcuts import render
from gestiones.models import Beneficio, CustomUser, Liquidacion, CargaFamiliar, Solicitud, Publicacion, Curso, Denuncia

def index(request):
    return render(request, 'index.html')  # Renderiza el template 'index.html'

def home(request):
    empresa = request.user.empresa
    cantidad_usuarios = CustomUser.objects.filter(empresa=empresa).count()
    cantidad_liquidaciones = Liquidacion.objects.filter(usuario__empresa=empresa).count()
    cantidad_cargas_familiares = CargaFamiliar.objects.filter(usuario__empresa=empresa).count()
    cantidad_solicitudes = Solicitud.objects.filter(colaborador__empresa=empresa).count()
    solicitudes_pendientes = Solicitud.objects.filter(colaborador__empresa=empresa, estado='Pendiente').count()
    solicitudes_aprobadas = Solicitud.objects.filter(colaborador__empresa=empresa, estado='Aprobada').count()
    solicitudes_rechazadas = Solicitud.objects.filter(colaborador__empresa=empresa, estado='Rechazada').count()
    
    # Nuevos contadores
    cantidad_cursos = Curso.objects.filter(supervisor__empresa=empresa).count()
    cantidad_beneficios = Beneficio.objects.filter(creado_por__empresa=empresa).count()
    cantidad_publicaciones = Publicacion.objects.filter(autor__empresa=empresa).count()
    
    # Contar denuncias por estado
    denuncias = Denuncia.objects.filter(denunciado__empresa=empresa)
    denuncias_pendientes = denuncias.filter(estado='pendiente').count()
    denuncias_revision = denuncias.filter(estado='revision').count()
    denuncias_resueltas = denuncias.filter(estado='resuelta').count()
    
    beneficios = Beneficio.objects.filter(creado_por__empresa=empresa)
    publicaciones = Publicacion.objects.all().order_by('-fecha_creacion')

    # Unir todos los datos en un solo diccionario
    context = {
        'cantidad_usuarios': cantidad_usuarios,
        'cantidad_liquidaciones': cantidad_liquidaciones,
        'cantidad_cargas_familiares': cantidad_cargas_familiares,
        'cantidad_solicitudes': cantidad_solicitudes,
        'solicitudes_pendientes': solicitudes_pendientes,
        'solicitudes_aprobadas': solicitudes_aprobadas,
        'solicitudes_rechazadas': solicitudes_rechazadas,
        'cantidad_cursos': cantidad_cursos,
        'cantidad_beneficios': cantidad_beneficios,
        'cantidad_publicaciones': cantidad_publicaciones,
        'denuncias_pendientes': denuncias_pendientes,
        'denuncias_revision': denuncias_revision,
        'denuncias_resueltas': denuncias_resueltas,
        'beneficios': beneficios,
        'publicaciones': publicaciones,
    }

    return render(request, 'home.html', context)
