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
