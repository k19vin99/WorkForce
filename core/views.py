from django.shortcuts import render
from gestiones.models import Beneficio, CustomUser, CargaFamiliar, Solicitud, Publicacion, Curso, Denuncia, Asistencia, Area, SolicitudVacaciones
from datetime import datetime, timedelta, date
from django.db.models import Count, Q

# Página principal
def index(request):
    return render(request, 'index/index.html') 

def home(request):
    today = date.today()  # Fecha actual
    empresa = request.user.empresa  # Empresa asociada al usuario actual

    # Usuarios por área: cuenta los usuarios en cada área, excluyendo a los administradores
    areas = Area.objects.filter(empresa=empresa)
    usuarios_por_area = {
        area.nombre: CustomUser.objects.filter(area=area).exclude(username__startswith='admin').count()
        for area in areas
    }

    # Total de usuarios en la empresa (excluyendo administradores)
    total_usuarios = CustomUser.objects.filter(empresa=empresa).exclude(username__startswith='admin').count()

    # Solicitudes por tipo y estado: cuenta las solicitudes agrupadas por tipo y clasifica por estado
    solicitudes_por_tipo = Solicitud.objects.filter(colaborador__empresa=empresa).values('tipo').annotate(
        total=Count('id'),
        pendientes=Count('id', filter=Q(estado='pendiente')),
        aprobadas=Count('id', filter=Q(estado='aprobada')),
        rechazadas=Count('id', filter=Q(estado='rechazada'))
    )

    # Totales de solicitudes por estado
    total_pendientes = sum(solicitud['pendientes'] for solicitud in solicitudes_por_tipo)
    total_aprobadas = sum(solicitud['aprobadas'] for solicitud in solicitudes_por_tipo)
    total_rechazadas = sum(solicitud['rechazadas'] for solicitud in solicitudes_por_tipo)

    # Denuncias por estado: cuenta las denuncias agrupadas por su estado
    denuncias_por_estado = Denuncia.objects.filter(denunciado__empresa=empresa).values('estado').annotate(
        total=Count('id')
    )

    # Totales de denuncias según su estado
    total_pendientes_denuncias = sum(
        denuncia['total'] for denuncia in denuncias_por_estado if denuncia['estado'] == 'pendiente'
    )
    total_resueltas_denuncias = sum(
        denuncia['total'] for denuncia in denuncias_por_estado if denuncia['estado'] == 'resuelta'
    )
    total_revision_denuncias = sum(
        denuncia['total'] for denuncia in denuncias_por_estado if denuncia['estado'] == 'revision'
    )

    # Beneficios disponibles para la empresa
    beneficios = Beneficio.objects.filter(creado_por__empresa=empresa)

    # Publicaciones ordenadas por fecha de creación (recientes primero)
    publicaciones = Publicacion.objects.all().order_by('-fecha_creacion')

    # Asistencia del usuario actual para el día de hoy
    asistencia = Asistencia.objects.filter(colaborador=request.user, fecha=datetime.now().date()).first()

    # Cálculo del tiempo trabajado si hay entrada y salida registradas
    tiempo_trabajado = None
    if asistencia and asistencia.hora_entrada and asistencia.hora_salida:
        entrada = datetime.combine(asistencia.fecha, asistencia.hora_entrada)
        salida = datetime.combine(asistencia.fecha, asistencia.hora_salida)
        tiempo_trabajado = salida - entrada

    # Contexto para pasar a la plantilla
    context = {
        'today': today,
        'usuarios_por_area': usuarios_por_area,
        'total_usuarios': total_usuarios,
        'solicitudes_por_tipo': solicitudes_por_tipo,
        'total_pendientes': total_pendientes,
        'total_aprobadas': total_aprobadas,
        'total_rechazadas': total_rechazadas,
        'total_pendientes_denuncias': total_pendientes_denuncias,
        'total_resueltas_denuncias': total_resueltas_denuncias,
        'total_revision_denuncias': total_revision_denuncias,
        'beneficios': beneficios,
        'publicaciones': publicaciones,
        'asistencia': asistencia, 
        'tiempo_trabajado': tiempo_trabajado 
    }

    # Renderiza la plantilla con el contexto generado
    return render(request, 'home/home.html', context)
