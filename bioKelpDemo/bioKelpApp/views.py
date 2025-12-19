from django.shortcuts import render, redirect
from django.db.models import Sum
from django.db.models import Q
from bioKelpApp.models import Produccion, Stock, Cliente
from .forms import ClienteForm
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


def lista_lotes(request):
    lotes = Lote.objects.select_related('especie', 'origen').all()
    return render(request, 'bioKelpApp/lotes/lista.html', {'lotes': lotes})

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

def detalle_lote(request, lote_id):
    lote = get_object_or_404(Lote, id=lote_id)
    movimientos = lote.movimientos.all()
    return render(request, 'bioKelpApp/lotes/detalle.html', {'lote': lote, 'movimientos': movimientos})

def historial_lote(request, lote_id):
    lote = get_object_or_404(Lote, id=lote_id)
    movimientos = lote.movimientos.order_by('fecha')  # cronológico asc
    return render(request, 'bioKelpApp/lotes/historial.html', {'lote': lote, 'movimientos': movimientos})

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

def historial_algas(request):
    especies = Especie.objects.order_by('nombre')
    return render(request, 'bioKelpApp/stock/historial_algas.html', {
        'especies': especies,
        'titulo': 'Historial de algas (por especie)'
    })

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




def renderRegistroApp(request):
    return render(request, 'templatesApp/registroApp.html')