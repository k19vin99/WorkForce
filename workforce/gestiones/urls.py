from django.urls import path
from . import views

urlpatterns = [
    #Usuarios
    path('registrar_usuario/', views.registrar_usuario, name='registrar_usuario'),
    path('colaboradores/', views.lista_colaboradores, name='lista_colaboradores'),
    path('colaboradores/editar/<int:pk>/', views.editar_colaborador, name='editar_colaborador'),
    path('colaboradores/eliminar/<int:pk>/', views.eliminar_colaborador, name='eliminar_colaborador'),
    path('colaboradores/exportar_excel/', views.exportar_colaboradores_excel, name='exportar_colaboradores_excel'),
    #Liquidaciones
    path('crear_liquidacion/', views.crear_liquidacion, name='crear_liquidacion'),
    path('visualizacion_liquidaciones/', views.visualizacion_liquidaciones, name='visualizacion_liquidaciones'),
    path('editar_liquidacion/<int:pk>/', views.editar_liquidacion, name='editar_liquidacion'),
    path('eliminar_liquidacion/<int:pk>/', views.eliminar_liquidacion, name='eliminar_liquidacion'),
    path('descargar_liquidacion/<int:pk>/', views.descargar_liquidacion_pdf, name='descargar_liquidacion'),
    #Cargas Familiares
    path('cargas/registrar/', views.registrar_carga, name='registrar_carga'),
    path('cargas/', views.listar_cargas, name='listar_cargas'),
    path('cargas/editar/<int:pk>/', views.editar_carga, name='editar_carga'),
    path('cargas/eliminar/<int:pk>/', views.eliminar_carga, name='eliminar_carga'),
    #Asistencia
    path('registro_asistencia/', views.registro_asistencia, name='registro_asistencia'),
    path('visualizacion_asistencia/', views.visualizacion_asistencia, name='visualizacion_asistencia'),
    #Solicitudes
    path('crear_solicitud/', views.crear_solicitud, name='crear_solicitud'),
    path('solicitudes/', views.lista_solicitudes, name='lista_solicitudes'),
    path('gestionar_solicitud/<int:pk>/', views.gestionar_solicitud, name='gestionar_solicitud'),
    path('solicitudes/<int:pk>/pdf/', views.descargar_comprobante, name='descargar_comprobante'),
    #Cursos
    path('cursos/', views.lista_cursos, name='lista_cursos'),
    path('cursos/crear/', views.crear_curso, name='crear_curso'),
    path('cursos/<int:curso_id>/agregar_modulo/', views.agregar_modulo, name='agregar_modulo'),
    path('modulos/<int:modulo_id>/', views.detalle_modulo, name='detalle_modulo'),
    path('modulos/<int:modulo_id>/agregar_comentario/', views.agregar_comentario, name='agregar_comentario'),
    path('cursos/<int:curso_id>/', views.detalle_curso, name='detalle_curso'),
    path('cursos/<int:curso_id>/editar_participantes/', views.editar_participantes, name='editar_participantes'),
    path('cursos/', views.lista_cursos_colaborador, name='lista_cursos_colaborador'),
    path('cursos/<int:curso_id>/', views.detalle_curso_colaborador, name='detalle_curso_colaborador'),
    path('modulos/<int:modulo_id>/editar/', views.editar_modulo, name='editar_modulo'),
    path('modulos/<int:modulo_id>/eliminar/', views.eliminar_modulo, name='eliminar_modulo'),
    #Beneficios
    path('beneficios/', views.lista_beneficios, name='lista_beneficios'),
    path('beneficios/crear/', views.crear_beneficio, name='crear_beneficio'),
    path('beneficios/<int:id>/editar/', views.editar_beneficio, name='editar_beneficio'),
    path('beneficios/<int:id>/eliminar/', views.eliminar_beneficio, name='eliminar_beneficio'),
    #Denuncias
    path('denuncias/', views.lista_denuncias, name='lista_denuncias'),
    path('denuncias/crear/', views.crear_denuncia, name='crear_denuncia'),
    path('denuncias/<int:pk>/', views.detalle_denuncia, name='detalle_denuncia'),  # Agrega esta línea
    path('denuncia_creada/', views.denuncia_creada, name='denuncia_creada'),  # Nueva URL para la confirmación
    #Publicaciones
    path('publicaciones/crear/', views.crear_publicacion, name='crear_publicacion'),

    path('contacto/', views.contacto, name='contacto'),
    path('success/', views.success, name='success'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/edit/photo/', views.edit_profile_photo, name='edit_profile_photo'),
    path('profile/change_password/', views.cambiar_contrasena, name='cambiar_contrasena'),
    path('buscar/', views.buscar, name='buscar'),
    
    
]
