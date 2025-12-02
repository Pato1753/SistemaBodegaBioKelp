from django import forms
from .models import Cliente

# Lista de opciones para el Select de Países (puedes agregar más)
PAISES_CHOICES = [
    ('', 'Seleccione un país'),
    ('Chile', 'Chile'),
    ('Argentina', 'Argentina'),
    ('Perú', 'Perú'),
    ('Bolivia', 'Bolivia'),
    ('Brasil', 'Brasil'),
    ('Colombia', 'Colombia'),
    ('Ecuador', 'Ecuador'),
    ('Venezuela', 'Venezuela'),
    ('Uruguay', 'Uruguay'),
    ('Paraguay', 'Paraguay'),
    ('México', 'México'),
    ('Estados Unidos', 'Estados Unidos'),
    ('España', 'España'),
    # Agrega el resto de tu lista aquí...
]

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = '__all__' # Usamos todos los campos del modelo

        # Aquí "disfrazamos" los inputs de Django para que tengan tu diseño
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'input-group', 
                'placeholder': 'Ingrese el nombre'
            }),
            'apellido': forms.TextInput(attrs={
                'class': 'input-group', 
                'placeholder': 'Ingrese el apellido'
            }),
            'rut': forms.TextInput(attrs={
                'class': 'input-group', 
                'placeholder': 'Ej: 12.345.678-9'
            }),
            'pais': forms.Select(choices=PAISES_CHOICES, attrs={
                'class': 'input-group',
                'id': 'pais'
            }),
            'correo': forms.EmailInput(attrs={
                'class': 'input-group', 
                'placeholder': 'ejemplo@correo.com'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'input-group', 
                'placeholder': '+56 9 1234 5678'
            }),
        }

    # Validación extra: Verificar si el RUT ya existe
    def clean_rut(self):
            rut = self.cleaned_data.get('rut')

            # 1. Limpieza básica: Quitamos puntos y guiones para quedarnos solo con números y K
            rut_limpio = rut.replace(".", "").replace("-", "").upper()

            # 2. Verificar formato: Debe tener al menos 8 caracteres (7 números + 1 DV)
            if len(rut_limpio) < 8:
                raise forms.ValidationError("El RUT es demasiado corto.")

            # Separamos el cuerpo del dígito verificador
            cuerpo = rut_limpio[:-1]
            dv_ingresado = rut_limpio[-1]

            # 3. Validar que el cuerpo sean solo números
            if not cuerpo.isdigit():
                raise forms.ValidationError("El cuerpo del RUT debe contener solo números.")

            # --- ALGORITMO MÓDULO 11 (Matemática Chilena) ---
            suma = 0
            multiplo = 2

            # Recorremos los números al revés
            for c in reversed(cuerpo):
                suma += int(c) * multiplo
                multiplo += 1
                if multiplo > 7:
                    multiplo = 2
            
            # Calculamos el dígito esperado
            dvr = 11 - (suma % 11)
            
            if dvr == 11:
                dv_calculado = '0'
            elif dvr == 10:
                dv_calculado = 'K'
            else:
                dv_calculado = str(dvr)

            # 4. Comparación final
            if dv_calculado != dv_ingresado:
                raise forms.ValidationError("El RUT ingresado no es válido (Dígito verificador incorrecto).")

            # 5. Verificamos duplicados (lo que ya tenías)
            # Excluimos al propio cliente si se estuviera editando (opcional, pero buena práctica)
            if Cliente.objects.filter(rut=rut).exists():
                raise forms.ValidationError("Este RUT ya está registrado en el sistema.")

            return rut