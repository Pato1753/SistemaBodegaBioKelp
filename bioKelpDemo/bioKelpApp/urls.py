from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

""" 
Eliminar usuarios de prueba (incluido superusuario)
Desde Django shell (RECOMENDADO)
python manage.py shell

from django.contrib.auth.models import User

User.objects.filter(is_superuser=True).delete()

biokelp
admin@biokelp.cl
biokelp123
"""


#bioKelpApp/urls.py

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='bioKelpApp/auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    path('', views.lista_lotes, name='lista_lotes'),
    path('lotes/crear/', views.crear_lote, name='crear_lote'),
    path('lotes/<int:lote_id>/editar/', views.editar_lote, name='editar_lote'),
    path('lotes/<int:lote_id>/', views.detalle_lote, name='detalle_lote'),
    path('lotes/<int:lote_id>/historial/', views.historial_lote, name='historial_lote'),
    path('lotes/<int:lote_id>/etapas/',views.actualizar_etapas_lote,name='actualizar_etapas_lote'),
    path('movimientos/registrar/', views.registrar_movimiento, name='registrar_movimiento'),
    path('stock/', views.stock_por_especie, name='stock_lista'),
    path('stock/especie/<int:especie_id>/', views.stock_por_especie, name='stock_por_especie'),
        # --- Usuarios (Administrador) ---
    path('usuarios/registrar/',views.registrar_usuario,name='registrar_usuario'),
    path('usuarios/',views.lista_usuarios,name='lista_usuarios'),

    # --- Producción (RF-01) ---

    # --- Lotes / Etapas (RF-02) ---
    
]
