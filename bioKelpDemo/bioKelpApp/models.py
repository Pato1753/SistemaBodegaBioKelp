
# Create your models here.
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import Group, Permission

from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model


class Usuario(models.Model):
    # Diagrama: PK int id_usuario
    id_usuario = models.AutoField(primary_key=True)
    # Diagrama: string nombre, apellido, correo, password, rol
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    
    ROL_CHOICES = [
        ('Administrador', 'Administrador'),
        ('Operario', 'Operario'),
        ('Comercial', 'Comercial'),
    ]
    rol = models.CharField(max_length=20, choices=ROL_CHOICES)
    
    # Diagrama: datetime fecha_creacion
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    class Meta:
        db_table = 'usuario'  # Opcional: para forzar el nombre exacto en la BD


class Cliente(models.Model):
    # Diagrama: PK int id_cliente
    id_cliente = models.AutoField(primary_key=True)
    # Diagrama: string nombre, rut, pais, correo, telefono
    nombre = models.CharField(max_length=150)
    apellido = models.CharField(max_length=150)
    rut = models.CharField(max_length=12, unique=True)
    pais = models.CharField(max_length=50)
    correo = models.EmailField()
    telefono = models.CharField(max_length=20)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'cliente'


class Stock(models.Model):
    # Diagrama: PK int id_stock
    id_stock = models.AutoField(primary_key=True)
    # Diagrama: string tipo_alga, float cantidad_disponible, string unidad
    tipo_alga = models.CharField(max_length=100)
    cantidad_disponible = models.FloatField()
    unidad = models.CharField(max_length=20)
    # Diagrama: date fecha_actualizacion
    fecha_actualizacion = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.tipo_alga} ({self.cantidad_disponible})"

    class Meta:
        db_table = 'stock'


class Pedido(models.Model):
    # Diagrama: PK int id_pedido
    id_pedido = models.AutoField(primary_key=True)
    
    # Diagrama: FK int id_cliente (Conectado a tabla Cliente)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, db_column='id_cliente')
    
    # Diagrama: date fecha_pedido
    fecha_pedido = models.DateField(default=timezone.now)
    
    # Diagrama: string estado (Enum)
    ESTADO_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('Enviado', 'Enviado'),
        ('Entregado', 'Entregado'),
    ]
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Pendiente')
    
    # Diagrama: float cantidad
    cantidad = models.FloatField()
    
    # Diagrama: string tipo_alga (OJO: No es FK según el texto del diagrama, es string)
    tipo_alga = models.CharField(max_length=100)

    def __str__(self):
        return f"Pedido {self.id_pedido}"

    class Meta:
        db_table = 'pedido'


class Produccion(models.Model):
    # Diagrama: PK int id_produccion
    id_produccion = models.AutoField(primary_key=True)
    
    # Diagrama: string tipo_alga
    tipo_alga = models.CharField(max_length=100)
    
    # Diagrama: float cantidad_humeda, cantidad_seca
    cantidad_humeda = models.FloatField()
    cantidad_seca = models.FloatField()
    
    # Diagrama: date fecha_cosecha
    fecha_cosecha = models.DateField()
    
    # Diagrama: string estado_proceso
    estado_proceso = models.CharField(max_length=50)
    
    # Diagrama: FK int id_usuario (Conectado a tabla Usuario)
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, db_column='id_usuario')

    def __str__(self):
        return f"Producción {self.id_produccion}"

    class Meta:
        db_table = 'produccion'


class Alerta(models.Model):
    # Diagrama: PK int id_alerta
    id_alerta = models.AutoField(primary_key=True)
    # Diagrama: string tipo_alerta, mensaje, estado
    tipo_alerta = models.CharField(max_length=50)
    mensaje = models.TextField()
    # Diagrama: datetime fecha_creacion
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20)

    # RELACIONES IMPLÍCITAS (Líneas del diagrama "notifica" y "monitorea")
    # Aunque no salen escritas en la caja azul de ALERTA, las líneas grises obligan a poner esto:
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True, blank=True, related_name='alertas')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, null=True, blank=True, related_name='alertas')

    class Meta:
        db_table = 'alerta'


class LogAuditoria(models.Model):
    # Diagrama: PK int id_log
    id_log = models.AutoField(primary_key=True)
    
    # Diagrama: FK int id_usuario (Conectado a tabla Usuario)
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, db_column='id_usuario')
    
    # Diagrama: string accion
    accion = models.CharField(max_length=100)
    
    # Diagrama: datetime fecha_accion
    fecha_accion = models.DateTimeField(auto_now_add=True)
    
    # Diagrama: string modulo, descripcion
    modulo = models.CharField(max_length=50)
    descripcion = models.TextField()

    class Meta:
        db_table = 'log_auditoria'

User = get_user_model()

FORMATO_CHOICES = [
    ('humedo', 'Húmedo'),
    ('seco', 'Seco'),
]


class Planta(models.Model):

    nombre = models.CharField(max_length=120, unique=True)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre


class Especie(models.Model):
    nombre = models.CharField(max_length=120, unique=True)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre


class Lote(models.Model):

    codigo = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,  
    )
    especie = models.ForeignKey(Especie, on_delete=models.PROTECT, related_name='lotes')
    origen = models.ForeignKey(Planta, on_delete=models.PROTECT, related_name='lotes')  # procedencia
    cantidad_humedo_kg = models.FloatField(default=0)   # cantidad en kg húmedo
    cantidad_seco_kg = models.FloatField(default=0)     # cantidad en kg seco (opcional)
    fecha_cosecha = models.DateField(null=True, blank=True)
    fecha_almacenamiento = models.DateField(null=True, blank=True)
    fecha_procesamiento = models.DateField(null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

class Movimiento(models.Model):
    TIPO_CHOICES = [
        ('produccion', 'Producción'),
        ('compra', 'Compra externa'),
        ('consumo', 'Consumo / Salida'),
        ('ajuste', 'Ajuste'),
        ('etapa_update', 'Actualización de etapa'),
    ]

    lote = models.ForeignKey(Lote, on_delete=models.CASCADE, related_name='movimientos', null=True, blank=True)
    especie = models.ForeignKey(Especie, on_delete=models.PROTECT, related_name='movimientos')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    cantidad_humedo_kg = models.FloatField(default=0)
    cantidad_seco_kg = models.FloatField(default=0)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    fecha = models.DateTimeField(default=timezone.now)
    descripcion = models.TextField(blank=True)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.tipo} {self.especie.nombre} {self.cantidad_seco_kg}kg(seco)'

    @staticmethod
    def stock_actual_por_especie(especie_id):

        from django.db.models import Sum, Q
        qs = Movimiento.objects.filter(especie_id=especie_id)
        suma_humedo_pos = qs.filter(tipo__in=['produccion', 'compra', 'ajuste']).aggregate(total=Sum('cantidad_humedo_kg'))['total'] or 0
        suma_humedo_neg = qs.filter(tipo='consumo').aggregate(total=Sum('cantidad_humedo_kg'))['total'] or 0
        suma_seco_pos = qs.filter(tipo__in=['produccion', 'compra', 'ajuste']).aggregate(total=Sum('cantidad_seco_kg'))['total'] or 0
        suma_seco_neg = qs.filter(tipo='consumo').aggregate(total=Sum('cantidad_seco_kg'))['total'] or 0
        return {
            'humedo_kg': suma_humedo_pos - suma_humedo_neg,
            'seco_kg': suma_seco_pos - suma_seco_neg,
        }


class Alerta(models.Model):
    NIVEL_CHOICES = [
        ('info', 'Información'),
        ('warning', 'Advertencia'),
        ('critical', 'Crítica'),
    ]
    especie = models.ForeignKey(
        Especie,
        on_delete=models.CASCADE,
        related_name='alertas',
        null=True,
        blank=True,
    )
    mensaje = models.TextField()
    nivel = models.CharField(max_length=10, choices=NIVEL_CHOICES, default='warning')
    creada_en = models.DateTimeField(auto_now_add=True)
    leida = models.BooleanField(default=False)

    class Meta:
        db_table = 'alerta'

    def __str__(self):
        especie_nombre = self.especie.nombre if self.especie else 'Sin especie'
        return f'{self.nivel.upper()} - {especie_nombre} - {self.mensaje[:40]}'

class Permiso(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

class RolPermiso(models.Model):
    rol = models.CharField(max_length=20)
    permiso = models.ForeignKey(Permiso, on_delete=models.CASCADE)
    

    
    