from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone

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