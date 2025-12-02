from django.urls import path
from . import views



urlpatterns = [
    path('', views.lista_lotes, name='lista_lotes'),
    path('lotes/crear/', views.crear_lote, name='crear_lote'),
    path('lotes/<int:lote_id>/editar/', views.editar_lote, name='editar_lote'),
    path('lotes/<int:lote_id>/', views.detalle_lote, name='detalle_lote'),
    path('lotes/<int:lote_id>/historial/', views.historial_lote, name='historial_lote'),
    path('movimientos/registrar/', views.registrar_movimiento, name='registrar_movimiento'),
    path('stock/', views.stock_por_especie, name='stock_lista'),
    path('stock/especie/<int:especie_id>/', views.stock_por_especie, name='stock_por_especie'),
]
