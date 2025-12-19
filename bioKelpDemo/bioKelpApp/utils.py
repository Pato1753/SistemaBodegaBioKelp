from django.core.exceptions import PermissionDenied
from .models import RolPermiso, LogAuditoria
from datetime import timedelta
from django.utils.timezone import now

def requiere_rol(roles_permitidos):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not hasattr(request.user, 'usuario'):
                raise PermissionDenied("Usuario no válido")

            if request.user.usuario.rol not in roles_permitidos:
                raise PermissionDenied("Acceso denegado")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def solo_admin(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.usuario.rol != 'Administrador':
            raise PermissionDenied("No tienes permisos")
        return view_func(request, *args, **kwargs)
    return wrapper

def tiene_permiso(usuario, permiso):
    return RolPermiso.objects.filter(
        rol=usuario.rol,
        permiso__nombre=permiso
    ).exists()

def tiene_permiso(usuario, permiso):
    return RolPermiso.objects.filter(
        rol=usuario.rol,
        permiso__nombre=permiso
    ).exists()

def vista_protegida(request):
    if not tiene_permiso(request.user.usuario, 'ver_auditoria'):
        raise PermissionDenied
    
def registrar_auditoria(usuario, accion, modulo, descripcion):
    LogAuditoria.objects.create(
        usuario=usuario,
        accion=accion,
        modulo=modulo,
        descripcion=descripcion
    )
    
def puede_editar(movimiento):
    return now() - movimiento.fecha <= timedelta(hours=24)