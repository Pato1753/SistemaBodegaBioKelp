from django.shortcuts import render, redirect
from django.db.models import Sum
from django.db.models import Q
from bioKelpApp.models import Produccion, Stock, Cliente
from django.core.exceptions import PermissionDenied
from .forms import ClienteForm
from django.contrib.auth.decorators import login_required, permission_required
from .utils import puede_editar, requiere_rol
from django.contrib.auth import authenticate, login, get_user_model
from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from bioKelpApp.forms import EtapasLoteForm
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError

# Create your views here.

def renderTMetrica(request):
    # --- LOGICA DE PRODUCCION (La que ya tenías) ---
    resumen = Produccion.objects.values('tipo_alga').annotate(
        total_humeda=Sum('cantidad_humeda'),
        total_seca=Sum('cantidad_seca')
    )
    
    suma = 0
    for x in resumen:
        cant_h = x["total_humeda"] or 0
        cant_s = x["total_seca"] or 0
        suma += cant_h + cant_s

    # --- NUEVA LOGICA DE STOCK (Alertas) ---
    umbral_minimo = 1000  # Definimos el límite de 1000 kg
    
    # "cantidad_disponible__lt" significa "Less Than" (Menor que)
    alertas_stock = Stock.objects.filter(cantidad_disponible__lt=umbral_minimo)

    # --- CONTEXTO UNIFICADO ---
    contexto = {
        'suma': suma,
        'resumen_algas': resumen,
        # Agregamos las nuevas variables para usar en el HTML
        'alertas_stock': alertas_stock, 
        'umbral': umbral_minimo 
    }

    return render(request, 'templatesApp/metrica.html', contexto)

# FUNCIONES DE CLIENTEEES --------------------------------------------

def renderClientes(request):
    return render(request,"templatesApp/clientes.html")

def renderVerClientes(request):
    # 1. Obtener todos los clientes base
    clientes = Cliente.objects.all()

    # 2. Obtener lista única de países para el filtro (sin repetir)
    paises = Cliente.objects.values_list('pais', flat=True).distinct().order_by('pais')

    # --- FILTROS ---
    
    # A) Búsqueda por texto (Nombre, Apellido o RUT)
    busqueda = request.GET.get('q')
    if busqueda:
        clientes = clientes.filter(
            Q(nombre__icontains=busqueda) | 
            Q(apellido__icontains=busqueda) | 
            Q(rut__icontains=busqueda)
        )

    # B) Filtro por País
    filtro_pais = request.GET.get('filtro_pais')
    if filtro_pais:
        clientes = clientes.filter(pais=filtro_pais)

    # C) Ordenamiento
    orden = request.GET.get('orden')
    if orden == 'az':
        clientes = clientes.order_by('nombre')
    elif orden == 'za':
        clientes = clientes.order_by('-nombre')
    elif orden == 'antiguo':
        clientes = clientes.order_by('id_cliente') # Asumiendo id auto-incremental
    elif orden == 'nuevo':
        clientes = clientes.order_by('-id_cliente')

    data = {
        'clientes': clientes,
        'paises': paises,
    }
    
    return render(request, "templatesApp/verCliente.html", data)

def eliminarCliente(request, id):
    # Buscamos el cliente por su ID (llave primaria)
    cliente = Cliente.objects.get(id_cliente=id)
    
    # Lo eliminamos de la base de datos
    cliente.delete()
    
    # Redirigimos a la lista para ver que desapareció
    return redirect('verCliente')


def renderRegistrarClientes(request):
    if request.method == 'POST':
        # Cargamos los datos que envió el usuario en el formulario
        form = ClienteForm(request.POST)
        
        if form.is_valid():
            form.save() # ¡Guardado y validado automáticamente!
            return redirect('verCliente')
    else:
        # Si es GET, mostramos el formulario vacío
        form = ClienteForm()

    # Enviamos el formulario (form) al HTML
    return render(request, "templatesApp/registrarCliente.html", {'form': form})
#------------------------------------------------------------


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from .models import Lote, Movimiento, Especie
from .forms import LoteForm, MovimientoForm
from django.shortcuts import render, get_object_or_404
from .models import Especie, Movimiento

@login_required
@permission_required('auth.view_lote', raise_exception=True)
def lista_lotes(request):
    lotes = Lote.objects.select_related('especie', 'origen').all()
    return render(request, 'bioKelpApp/lotes/lista.html', {'lotes': lotes})

@login_required
@permission_required('auth.add_lote', raise_exception=True)
def crear_lote(request):
    if request.method == 'POST':
        form = LoteForm(request.POST)
        if form.is_valid():
            lote = form.save()
            messages.success(request, 'Lote creado correctamente.')
            return redirect('bioKelpApp:detalle_lote', lote_id=lote.id)
    else:
        form = LoteForm()
    return render(request, 'bioKelpApp/lotes/form.html', {'form': form, 'titulo': 'Crear Lote'})

@login_required
@permission_required('auth.change_lote', raise_exception=True)
def editar_lote(request, lote_id):
    lote = get_object_or_404(Lote, id=lote_id)
    if request.method == 'POST':
        form = LoteForm(request.POST, instance=lote)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lote actualizado correctamente.')
            return redirect('bioKelpApp:detalle_lote', lote_id=lote.id)
    else:
        form = LoteForm(instance=lote)
    return render(request, 'bioKelpApp/lotes/form.html', {'form': form, 'titulo': 'Editar Lote'})

@login_required
@permission_required('auth.view_lote', raise_exception=True)
def detalle_lote(request, lote_id):
    lote = get_object_or_404(Lote, id=lote_id)
    movimientos = lote.movimientos.all()
    return render(request, 'bioKelpApp/lotes/detalle.html', {'lote': lote, 'movimientos': movimientos})

@login_required
@permission_required('auth.view_lote', raise_exception=True)
def historial_lote(request, lote_id):
    lote = get_object_or_404(Lote, id=lote_id)
    movimientos = lote.movimientos.order_by('fecha')  # cronológico asc
    return render(request, 'bioKelpApp/lotes/historial.html', {'lote': lote, 'movimientos': movimientos})

@login_required
@permission_required('auth.view_especie', raise_exception=True)
def stock_por_especie(request, especie_id=None):
    especies = Especie.objects.all()
    selected = None
    stock = {}
    if especie_id:
        selected = get_object_or_404(Especie, id=especie_id)
        stock = Movimiento.stock_actual_por_especie(selected.id)
    return render(request, 'bioKelpApp/stock/por_especie.html', {
        'especies': especies,
        'selected': selected,
        'stock': stock
    })
@login_required
@permission_required('auth.add_movimiento', raise_exception=True)
def registrar_movimiento(request):
    if request.method == 'POST':
        form = MovimientoForm(request.POST)
        if form.is_valid():
            movimiento = form.save(commit=False)
            movimiento.usuario = request.user if request.user.is_authenticated else None
            movimiento.save()
            messages.success(request, 'Movimiento registrado.')
            return redirect(reverse('bioKelpApp:lista_lotes'))
    else:
        form = MovimientoForm()
    return render(request, 'bioKelpApp/movimientos/form.html', {'form': form})

@login_required
@permission_required('auth.view_algas', raise_exception=True)
def historial_algas(request):
    especies = Especie.objects.order_by('nombre')
    return render(request, 'bioKelpApp/stock/historial_algas.html', {
        'especies': especies,
        'titulo': 'Historial de algas (por especie)'
    })
    
@login_required
@permission_required('auth.view_especie', raise_exception=True)
def historial_por_especie(request, especie_id):
    especie = get_object_or_404(Especie, pk=especie_id)

    movimientos = (Movimiento.objects
                   .select_related('lote', 'especie', 'usuario')
                   .filter(especie=especie)
                   .order_by('-fecha'))

    stock = Movimiento.stock_actual_por_especie(especie.id)

    return render(request, 'bioKelpApp/stock/historial_por_especie.html', {
        'especie': especie,
        'movimientos': movimientos,
        'stock': stock,
        'titulo': f'Historial: {especie.nombre}',
    })


""" RF-02 — Registrar procedencia y etapas del lote (trazabilidad) """


def validar_orden_etapas(cosecha, almacenamiento, procesamiento):
    if cosecha and almacenamiento and almacenamiento < cosecha:
        raise ValidationError('La fecha de almacenamiento no puede ser anterior a la cosecha')

    if almacenamiento and procesamiento and procesamiento < almacenamiento:
        raise ValidationError('La fecha de procesamiento no puede ser anterior al almacenamiento')


@login_required
@permission_required('auth.change_lote', raise_exception=True)
def actualizar_etapas_lote(request, lote_id):

    lote = Lote.objects.get(id=lote_id)

    if request.method == 'POST':
        form = EtapasLoteForm(request.POST, instance=lote)

        if form.is_valid():
            form.save()

            Movimiento.objects.create(
                lote=lote,
                especie=lote.especie,
                tipo='etapa_update',
                usuario=request.user,
                descripcion=f'''
                    Cosecha: {lote.fecha_cosecha or "-"},
                    Almacenamiento: {lote.fecha_almacenamiento or "-"},
                    Procesamiento: {lote.fecha_procesamiento or "-"}
                '''
            )

            return redirect('detalle_lote', lote.id)

    else:
        form = EtapasLoteForm(instance=lote)

    return render(request, 'bioKelpApp/lotes/etapas.html', {
        'lote': lote,
        'form': form
    })


""" historial = Movimiento.objects.filter(
    lote=lote,
    tipo='etapa_update'
).order_by('fecha') """


@login_required
@permission_required('auth.view_admin', raise_exception=True)
def vista_admin(request):
    return render(request, 'admin/dashboard.html')


@login_required
@permission_required('auth.add_pedido', raise_exception=True)
def crear_pedido(request):
    return render(request, 'bioKelpApp/pedidos/crearPedido.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user:
            login(request, user)
            return redirect('dashboard')

        return render(request, 'bioKelpApp/auth/login.html', {
            'error': 'Credenciales inválidas'
        })

    return render(request, 'bioKelpApp/auth/login.html')
        



User = get_user_model()


@login_required
@permission_required('auth.add_user', raise_exception=True)
def registrar_usuario(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        grupo_nombre = request.POST.get('grupo')

        # Escenario 2 – Validación de datos obligatorios
        if not username or not password or not grupo_nombre:
            return render(request, 'bioKelpApp/auth/registrar.html', {
                'error': 'Todos los campos son obligatorios'
            })

        if User.objects.filter(username=username).exists():
            return render(request, 'bioKelpApp/auth/registrar.html', {
                'error': 'El nombre de usuario ya existe'
            })

        # Crear usuario
        user = User.objects.create_user(
            username=username,
            password=password,
            is_active=True
        )

        # Asignar grupo (rol)
        try:
            grupo = Group.objects.get(name=grupo_nombre)
            user.groups.add(grupo)
        except Group.DoesNotExist:
            user.delete()
            return render(request, 'bioKelpApp/auth/registrar.html', {
                'error': 'Grupo inválido'
            })

        return redirect('lista_usuarios')

    # GET
    grupos = Group.objects.all()
    return render(request, 'bioKelpApp/auth/registrar.html', {
        'grupos': grupos
    })

@login_required
@permission_required('auth.view_user', raise_exception=True)
def lista_usuarios(request):
    usuarios = User.objects.all()
    return render(request, 'bioKelpApp/auth/lista_usuarios.html', {
        'usuarios': usuarios
    })
