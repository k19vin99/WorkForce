from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import CustomUserCreationForm, LiquidacionSueldoForm, EditarUsuarioForm, CargaFamiliarForm, SolicitudForm, ContactForm, EditProfileForm, EditProfilePhotoForm, PasswordChangeForm, CursoForm, ModuloForm, ComentarioForm, EditarParticipantesForm, BeneficioForm, DenunciaForm, EvidenciaFormset, NotaDenunciaForm, PublicacionForm
import os
from django.conf import settings
from .models import Liquidacion, CustomUser, CargaFamiliar, Asistencia, Solicitud, Curso, Modulo, Comentario, Beneficio, Area, Denuncia, EvidenciaDenuncia
from django.http import HttpResponse
from xhtml2pdf import pisa
from django.template.loader import get_template
import openpyxl
from datetime import datetime, timedelta
from django.urls import reverse
from django.core.mail import send_mail
from django.db.models import Q
from django.contrib.auth.models import Group
from django.contrib.auth import update_session_auth_hash

def is_hr_analyst(user):
    return user.area and user.area.nombre == 'Recursos Humanos' and user.cargo == 'Analista de Personas'

#Función para separar usuarios por grupo supervisores o colaboradores
def is_supervisor(user):
    return user.groups.filter(name='supervisores').exists()

#Vista para buscar
@login_required
def buscar(request):
    query = request.GET.get('q')
    
    # Buscar en Solicitudes
    resultados_solicitudes = Solicitud.objects.filter(
        Q(tipo__icontains=query) | 
        Q(descripcion__icontains=query) | 
        Q(estado__icontains=query),
        colaborador__empresa=request.user.empresa
    )
    
    # Buscar en Cursos
    resultados_cursos = Curso.objects.filter(
        Q(nombre__icontains=query) |
        Q(descripcion__icontains=query),
        participantes__empresa=request.user.empresa
    ).distinct()
    
    # Buscar en Liquidaciones
    resultados_liquidaciones = Liquidacion.objects.filter(
        Q(usuario__username__icontains=query) | 
        Q(usuario__first_name__icontains=query) |  
        Q(usuario__last_name__icontains=query) |  
        Q(sueldo_base__icontains=query) |
        Q(fecha__icontains=query),
        usuario__empresa=request.user.empresa
    )

    context = {
        'resultados_solicitudes': resultados_solicitudes,
        'resultados_cursos': resultados_cursos,
        'resultados_liquidaciones': resultados_liquidaciones,
    }

    return render(request, 'gestiones/buscar/busqueda.html', context)

#Vista usuarios
@login_required
def registrar_usuario(request):
    if not is_supervisor(request.user):
        return redirect('home')  # Redirige si el usuario no es un supervisor

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.empresa = request.user.empresa  # Asigna la empresa del supervisor al nuevo usuario
            new_user.save()

            # Asigna el grupo seleccionado al nuevo usuario
            grupo = form.cleaned_data['grupo']
            group = Group.objects.get(name=grupo)
            new_user.groups.add(group)

            return redirect('home')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'gestiones/usuarios/registrar_usuario.html', {'form': form})

@login_required
@user_passes_test(is_supervisor)
def lista_colaboradores(request):
    colaboradores = CustomUser.objects.filter(empresa=request.user.empresa)
    return render(request, 'gestiones/usuarios/lista_colaboradores.html', {'colaboradores': colaboradores})

@login_required
@user_passes_test(is_supervisor)  # Solo los supervisores pueden acceder a esta vista
def editar_colaborador(request, pk):
    colaborador = get_object_or_404(CustomUser, pk=pk)
    
    if request.method == 'POST':
        form = EditarUsuarioForm(request.POST, instance=colaborador)
        if form.is_valid():
            form.save()
            return redirect('lista_colaboradores')  # Redirige a la lista de colaboradores después de guardar
    else:
        form = EditarUsuarioForm(instance=colaborador)
    
    return render(request, 'gestiones/usuarios/editar_colaborador.html', {'form': form, 'colaborador': colaborador})


@login_required
@user_passes_test(is_supervisor)
def eliminar_colaborador(request, pk):
    colaborador = get_object_or_404(CustomUser, pk=pk)
    
    if request.method == 'POST':
        colaborador.delete()
        return redirect('lista_colaboradores')
    
    return render(request, 'gestiones/usuarios/eliminar_colaborador.html', {'colaborador': colaborador})

@login_required
@user_passes_test(is_supervisor)
def exportar_colaboradores_excel(request):
    colaboradores = CustomUser.objects.filter(empresa=request.user.empresa)
    
    # Crear un libro de trabajo y una hoja
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Colaboradores'

    # Escribir encabezados
    ws.append(['Username', 'Nombre', 'Apellido', 'Email', 'Cargo'])

    # Escribir datos de colaboradores
    for colaborador in colaboradores:
        ws.append([colaborador.username, colaborador.first_name, colaborador.last_name, colaborador.email, colaborador.cargo])
    
    # Configurar la respuesta HTTP para descargar el archivo Excel
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=colaboradores.xlsx'
    wb.save(response)
    
    return response

#Vistas Liquidaciones
@login_required
@user_passes_test(is_supervisor)
def crear_liquidacion(request):
    if request.method == 'POST':
        form = LiquidacionSueldoForm(request.POST, user=request.user)
        if form.is_valid():
            liquidacion = form.save(commit=False)
            liquidacion.empresa = request.user.empresa  # Asigna la empresa del usuario que crea la liquidación
            liquidacion.save()
            return redirect('visualizacion_liquidaciones')
    else:
        form = LiquidacionSueldoForm(user=request.user)
    
    return render(request, 'gestiones/liquidaciones/crear_liquidacion.html', {'form': form})

@login_required
@user_passes_test(is_supervisor)
def editar_liquidacion(request, pk):
    liquidacion = get_object_or_404(Liquidacion, pk=pk)
    if request.method == 'POST':
        form = LiquidacionSueldoForm(request.POST, instance=liquidacion)
        if form.is_valid():
            form.save()
            return redirect('visualizacion_liquidaciones')
    else:
        form = LiquidacionSueldoForm(instance=liquidacion)
    return render(request, 'gestiones/liquidaciones/editar_liquidacion.html', {'form': form, 'liquidacion': liquidacion})

@login_required
def visualizacion_liquidaciones(request):
    if is_supervisor(request.user):
        # Filtra las liquidaciones de la empresa a la que pertenece el usuario supervisor
        liquidaciones = Liquidacion.objects.filter(usuario__empresa=request.user.empresa)
    else:
        # Filtra solo las liquidaciones del usuario que está viendo la página
        liquidaciones = Liquidacion.objects.filter(usuario=request.user)
    
    return render(request, 'gestiones/liquidaciones/visualizacion_liquidaciones.html', {'liquidaciones': liquidaciones})


@login_required
@user_passes_test(is_supervisor)
def eliminar_liquidacion(request, pk):
    liquidacion = get_object_or_404(Liquidacion, pk=pk)
    if request.method == 'POST':
        liquidacion.delete()
        return redirect('visualizacion_liquidaciones')
    return render(request, 'gestiones/liquidaciones/eliminar_liquidacion.html', {'liquidacion': liquidacion})

@login_required
def descargar_liquidacion_pdf(request, pk):
    try:
        if request.user.groups.filter(name='supervisores').exists():
            liquidacion = get_object_or_404(Liquidacion, pk=pk, usuario__empresa=request.user.empresa)
        else:
            liquidacion = get_object_or_404(Liquidacion, pk=pk, usuario=request.user)

        # Calcula el total de haberes y descuentos
        total_haberes = liquidacion.sueldo_base + liquidacion.gratificacion + liquidacion.colacion + liquidacion.movilizacion
        total_descuentos = liquidacion.afp + liquidacion.salud + liquidacion.seguro_mutual

        template_path = 'gestiones/liquidaciones/liquidacion_pdf.html'
        context = {
            'liquidacion': liquidacion,
            'total_haberes': total_haberes,
            'total_descuentos': total_descuentos,
        }

        response = HttpResponse(content_type='application/pdf')
        nombre_archivo = f'liquidacion_{liquidacion.id}.pdf'
        response['Content-Disposition'] = f'inline; filename="{nombre_archivo}"'

        template = get_template(template_path)
        html = template.render(context)
        pisa_status = pisa.CreatePDF(html, dest=response)

        if pisa_status.err:
            return HttpResponse('Ocurrieron algunos errores durante la generación del PDF <pre>' + html + '</pre>')

        return response
    except Liquidacion.DoesNotExist:
        return HttpResponse('No se encontró la liquidación solicitada.', status=404)

#Vistas Cargas Familiares
@login_required
@user_passes_test(is_supervisor)
def registrar_carga(request):
    if request.method == 'POST':
        form = CargaFamiliarForm(request.POST, user=request.user)  # Pasa el usuario al formulario
        if form.is_valid():
            form.save()
            return redirect('listar_cargas')
    else:
        form = CargaFamiliarForm(user=request.user)  # Pasa el usuario al formulario
    return render(request, 'gestiones/cargas_familiares/registrar_carga.html', {'form': form})

@login_required
def listar_cargas(request):
    if is_supervisor(request.user):
        # Si el usuario es supervisor, muestra todas las cargas de su empresa
        cargas = CargaFamiliar.objects.filter(usuario__empresa=request.user.empresa)
    else:
        # Si el usuario es colaborador, muestra solo sus cargas
        cargas = CargaFamiliar.objects.filter(usuario=request.user)
    
    return render(request, 'gestiones/cargas_familiares/listar_cargas.html', {'cargas': cargas})

@login_required
def editar_carga(request, pk):
    carga = get_object_or_404(CargaFamiliar, pk=pk)
    if request.method == 'POST':
        form = CargaFamiliarForm(request.POST, instance=carga)
        if form.is_valid():
            form.save()
            return redirect('listar_cargas')
    else:
        form = CargaFamiliarForm(instance=carga)
    return render(request, 'gestiones/cargas_familiares/editar_carga.html', {'form': form})

@login_required
def eliminar_carga(request, pk):
    carga = get_object_or_404(CargaFamiliar, pk=pk)
    if request.method == 'POST':
        carga.delete()
        return redirect('listar_cargas')
    return render(request, 'gestiones/cargas_familiares/eliminar_carga.html', {'carga': carga})

#Vistas Asistencia
@login_required
def registro_asistencia(request):
    asistencia = Asistencia.objects.filter(colaborador=request.user, fecha=datetime.now().date()).first()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if not asistencia:
            asistencia = Asistencia(colaborador=request.user)

        current_time = datetime.now()

        if action == 'entrada':
            asistencia.hora_entrada = current_time.time()
        elif action == 'salida':
            asistencia.hora_salida = current_time.time()

        asistencia.save()
        return redirect('visualizacion_asistencia')
    
    tiempo_trabajado = None
    if asistencia and asistencia.hora_entrada and asistencia.hora_salida:
        entrada = datetime.combine(asistencia.fecha, asistencia.hora_entrada)
        salida = datetime.combine(asistencia.fecha, asistencia.hora_salida)
        tiempo_trabajado = salida - entrada
    
    return render(request, 'gestiones/asistencia/registro_asistencia.html', {
        'asistencia': asistencia,
        'tiempo_trabajado': tiempo_trabajado
    })

@login_required
def visualizacion_asistencia(request):
    if is_supervisor(request.user):
        # Filtrar por la empresa del supervisor
        asistencias = Asistencia.objects.filter(colaborador__empresa=request.user.empresa)
    else:
        asistencias = Asistencia.objects.filter(colaborador=request.user)
    
    return render(request, 'gestiones/asistencia/visualizacion_asistencia.html', {'asistencias': asistencias})

#Vistas Solicitudes
@login_required
def crear_solicitud(request):
    if request.method == 'POST':
        form = SolicitudForm(request.POST)
        if form.is_valid():
            solicitud = form.save(commit=False)
            solicitud.colaborador = request.user
            solicitud.save()
            return redirect('lista_solicitudes')
    else:
        form = SolicitudForm()
    return render(request, 'gestiones/solicitudes/crear_solicitud.html', {'form': form})

@login_required
def lista_solicitudes(request):
    if request.user.groups.filter(name='supervisores').exists():
        # Filtrar por la empresa del supervisor
        solicitudes = Solicitud.objects.filter(colaborador__empresa=request.user.empresa)
        is_supervisor = True
    else:
        solicitudes = Solicitud.objects.filter(colaborador=request.user)
        is_supervisor = False

    return render(request, 'gestiones/solicitudes/lista_solicitudes.html', {
        'solicitudes': solicitudes,
        'is_supervisor': is_supervisor
    })

@login_required
def gestionar_solicitud(request, pk):
    solicitud = get_object_or_404(Solicitud, pk=pk)
    if request.method == 'POST':
        if 'aprobar' in request.POST:
            solicitud.estado = 'aprobada'
        elif 'rechazar' in request.POST:
            solicitud.estado = 'rechazada'
        solicitud.save()
        return redirect('lista_solicitudes')
    return render(request, 'gestiones/solicitudes/gestionar_solicitud.html', {'solicitud': solicitud})

@login_required
def descargar_comprobante(request, pk):
    solicitud = get_object_or_404(Solicitud, pk=pk)
    template_path = 'gestiones/solicitudes/comprobante_solicitud.html'
    context = {'solicitud': solicitud}
    
    # Cargar la plantilla y renderizarla con el contexto
    template = get_template(template_path)
    html = template.render(context)
    
    # Crear un objeto de respuesta como PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Comprobante_Solicitud_{solicitud.id}.pdf"'
    
    # Generar el PDF
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    # Verificar si hubo errores
    if pisa_status.err:
        return HttpResponse('Error al generar el PDF: <pre>' + html + '</pre>')
    
    return response

def contacto(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            motivo_contacto = form.cleaned_data['motivo_contacto']
            nombre = form.cleaned_data['nombre']
            apellido = form.cleaned_data['apellido']
            numero_telefono = form.cleaned_data['numero_telefono']
            correo = form.cleaned_data['correo']
            nombre_empresa = form.cleaned_data['nombre_empresa']
            cantidad_colaboradores = form.cleaned_data['cantidad_colaboradores']
            cargo = form.cleaned_data['cargo']
            area_desempeno = form.cleaned_data['area_desempeno']
            rubro = form.cleaned_data['rubro']
            mensaje = form.cleaned_data['mensaje']
            
            send_mail(
                f'Contacto desde la web: {motivo_contacto}',
                f'Nombre: {nombre} {apellido}\nTeléfono: {numero_telefono}\nCorreo: {correo}\nEmpresa: {nombre_empresa}\nColaboradores: {cantidad_colaboradores}\nCargo: {cargo}\nÁrea de Desempeño: {area_desempeno}\nRubro: {rubro}\nMensaje: {mensaje}',
                'tu_email@gmail.com',
                ['destino_email@gmail.com'],
                fail_silently=False,
            )
            
            return redirect('success')
    else:
        form = ContactForm()
    
    return render(request, 'gestiones/contacto/contacto.html', {'form': form})

def success(request):
    return render(request, 'gestiones/contacto/success.html')

# Vista del perfil de usuario
@login_required
def profile(request):
    
    user = request.user
    return render(request, 'gestiones/profile/profile.html', {'user': user})

# Vista para editar el perfil
@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = EditProfileForm(instance=request.user)
    
    return render(request, 'gestiones/profile/edit_profile.html', {'form': form})

# Vista para editar la foto de perfil
@login_required
def edit_profile_photo(request):
    if request.method == 'POST':
        form = EditProfilePhotoForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = EditProfilePhotoForm(instance=request.user)
    
    return render(request, 'gestiones/profile/edit_profile_photo.html', {'form': form})

# Vista para cambiar la contraseña
@login_required
def cambiar_contrasena(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Mantiene al usuario conectado
            return redirect('profile')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'gestiones/profile/cambiar_contrasena.html', {'form': form})

#Vistas Cursos
@login_required
@user_passes_test(lambda u: u.groups.filter(name='supervisores').exists())
def crear_curso(request):
    if request.method == 'POST':
        form = CursoForm(request.POST, supervisor=request.user)
        if form.is_valid():
            curso = form.save(commit=False)
            curso.supervisor = request.user
            curso.save()
            form.save_m2m()  # Save the M2M relationships
            return redirect('detalle_curso', curso.id)
    else:
        form = CursoForm(supervisor=request.user)
    return render(request, 'gestiones/cursos/crear_curso.html', {'form': form})

@login_required
def detalle_curso(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    modulos = curso.modulos.all()
    participantes = curso.participantes.all()

    return render(request, 'gestiones/cursos/detalle_curso.html', {
        'curso': curso,
        'modulos': modulos,
        'participantes': participantes,
    })

@login_required
@user_passes_test(lambda u: u.groups.filter(name='supervisores').exists())
def agregar_modulo(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    if request.method == 'POST':
        form = ModuloForm(request.POST, request.FILES)
        if form.is_valid():
            modulo = form.save(commit=False)
            modulo.curso = curso
            modulo.save()
            return redirect('detalle_curso', curso.id)
    else:
        form = ModuloForm()
    return render(request, 'gestiones/cursos/agregar_modulo.html', {'form': form, 'curso': curso})

@login_required
def agregar_comentario(request, modulo_id):
    modulo = get_object_or_404(Modulo, id=modulo_id)
    if request.method == 'POST':
        form = ComentarioForm(request.POST)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.usuario = request.user
            comentario.modulo = modulo
            comentario.save()
            return redirect('detalle_modulo', modulo.id)
    else:
        form = ComentarioForm()
    return render(request, 'gestiones/modulos/agregar_comentario.html', {'form': form, 'modulo': modulo})

@login_required
def detalle_modulo(request, modulo_id):
    modulo = get_object_or_404(Modulo, id=modulo_id)
    comentarios = modulo.comentarios.all()
    return render(request, 'gestiones/modulos/detalle_modulo.html', {'modulo': modulo, 'comentarios': comentarios})

@login_required
def lista_cursos(request):
    if request.user.groups.filter(name='supervisores').exists():
        # Si el usuario es supervisor, muestra todos los cursos de su empresa
        cursos = Curso.objects.filter(supervisor__empresa=request.user.empresa)
    else:
        # Si el usuario es colaborador, muestra solo los cursos en los que participa
        cursos = Curso.objects.filter(participantes=request.user)

    return render(request, 'gestiones/cursos/lista_cursos.html', {'cursos': cursos})

@login_required
def detalle_curso_colaborador(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id, participantes=request.user)
    modulos = curso.modulos.all()

    if request.method == 'POST':
        form = ComentarioForm(request.POST)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.usuario = request.user
            comentario.save()
            return redirect('detalle_curso_colaborador', curso_id=curso_id)
    else:
        form = ComentarioForm()

    return render(request, 'gestiones/cursos/detalle_curso_colaborador.html', {
        'curso': curso,
        'modulos': modulos,
        'form': form
    })

@login_required
@user_passes_test(is_supervisor)
def editar_modulo(request, modulo_id):
    modulo = get_object_or_404(Modulo, id=modulo_id)
    if request.method == 'POST':
        form = ModuloForm(request.POST, request.FILES, instance=modulo)
        if form.is_valid():
            form.save()
            return redirect('detalle_curso', curso_id=modulo.curso.id)
    else:
        form = ModuloForm(instance=modulo)
    return render(request, 'gestiones/cursos/editar_modulo.html', {'form': form, 'modulo': modulo})

@login_required
def lista_cursos_colaborador(request):
    cursos = request.user.cursos.all()  # Obtiene los cursos donde el usuario es participante
    return render(request, 'gestiones/cursos/lista_cursos_colaborador.html', {'cursos': cursos})

@login_required
@user_passes_test(is_supervisor)
def eliminar_modulo(request, modulo_id):
    modulo = get_object_or_404(Modulo, id=modulo_id)
    curso_id = modulo.curso.id
    modulo.delete()
    return redirect('detalle_curso', curso_id=curso_id)

@login_required
def editar_participantes(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)

    if request.method == 'POST':
        form = EditarParticipantesForm(request.POST, instance=curso)
        if form.is_valid():
            form.save()
            return redirect('detalle_curso', curso_id=curso.id)
    else:
        form = EditarParticipantesForm(instance=curso)

    return render(request, 'gestiones/cursos/editar_participantes.html', {
        'curso': curso,
        'form': form,
    })

#Vistas Beneficios
def lista_beneficios(request):
    empresa = request.user.empresa
    beneficios = Beneficio.objects.filter(creado_por__empresa=empresa)

    context = {
        'beneficios': beneficios
    }

    return render(request, 'gestiones/beneficios/lista_beneficios.html', context)

@login_required
def crear_beneficio(request):
    if request.method == 'POST':
        form = BeneficioForm(request.POST, request.FILES)
        if form.is_valid():
            beneficio = form.save(commit=False)
            beneficio.creado_por = request.user
            beneficio.save()
            return redirect('lista_beneficios')
    else:
        form = BeneficioForm()
    return render(request, 'gestiones/beneficios/crear_beneficio.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.groups.filter(name='supervisores').exists())
def editar_beneficio(request, id):
    beneficio = get_object_or_404(Beneficio, id=id)

    if request.method == 'POST':
        form = BeneficioForm(request.POST, request.FILES, instance=beneficio)
        if form.is_valid():
            form.save()
            return redirect('lista_beneficios')
    else:
        form = BeneficioForm(instance=beneficio)

    return render(request, 'gestiones/beneficios/editar_beneficio.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.groups.filter(name='supervisores').exists())
def eliminar_beneficio(request, id):
    beneficio = get_object_or_404(Beneficio, id=id)

    if request.method == 'POST':
        beneficio.delete()
        return redirect('lista_beneficios')

    return render(request, 'gestiones/beneficios/eliminar_beneficio_confirmacion.html', {'beneficio': beneficio})



@login_required
def crear_denuncia(request):
    if request.method == 'POST':
        form = DenunciaForm(request.POST)
        formset = EvidenciaFormset(request.POST, request.FILES)
        
        if form.is_valid() and formset.is_valid():
            # Guardar la denuncia
            denuncia = form.save(commit=False)
            denuncia.denunciante = request.user  # Asignar el denunciante
            denuncia.save()

            # Guardar las evidencias relacionadas
            for evidencia_form in formset:
                if evidencia_form.cleaned_data.get('archivo'):  # Si se ha proporcionado un archivo
                    evidencia = evidencia_form.save(commit=False)
                    evidencia.denuncia = denuncia  # Relacionar con la denuncia
                    evidencia.save()

            return redirect('denuncia_creada')  # Redirige a una página de confirmación
    else:
        form = DenunciaForm()
        formset = EvidenciaFormset(queryset=EvidenciaDenuncia.objects.none())  # Formset vacío

    return render(request, 'gestiones/denuncias/crear_denuncia.html', {'form': form, 'formset': formset})

def denuncia_creada(request):
    return render(request, 'gestiones/denuncias/denuncia_creada.html')
                  
@login_required
def lista_denuncias(request):
    # Si el usuario es de Recursos Humanos y tiene el cargo de Analista de Personas
    if request.user.area.nombre == 'Recursos Humanos' and request.user.cargo == 'Analista de Personas':
        # Los usuarios de Recursos Humanos pueden ver todas las denuncias
        denuncias = Denuncia.objects.all()
    else:
        # Otros usuarios solo pueden ver las denuncias que ellos mismos han creado
        denuncias = Denuncia.objects.filter(denunciante=request.user)

    return render(request, 'gestiones/denuncias/lista_denuncias.html', {'denuncias': denuncias})

@login_required
def detalle_denuncia(request, pk):
    denuncia = get_object_or_404(Denuncia, pk=pk)
    notas = denuncia.notas.all()  # Notas relacionadas con la denuncia

    if request.method == 'POST':
        form = NotaDenunciaForm(request.POST)
        if form.is_valid():
            nota = form.save(commit=False)
            nota.denuncia = denuncia
            nota.usuario = request.user
            nota.save()
            return redirect('detalle_denuncia', pk=denuncia.pk)
    else:
        form = NotaDenunciaForm()

    return render(request, 'gestiones/denuncias/detalle_denuncia.html', {
        'denuncia': denuncia,
        'form': form,
        'notas': notas,
    })

@login_required
def crear_publicacion(request):
    if request.method == 'POST':
        form = PublicacionForm(request.POST, request.FILES)  # Agrega request.FILES
        if form.is_valid():
            publicacion = form.save(commit=False)
            publicacion.autor = request.user
            publicacion.save()
            return redirect('home')  # Redirige a la página de inicio después de crear la publicación
    else:
        form = PublicacionForm()

    return render(request, 'gestiones/publicaciones/crear_publicacion.html', {'form': form})