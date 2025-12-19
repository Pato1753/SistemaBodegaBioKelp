from django.db import migrations

def crear_roles(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')

    operario, _ = Group.objects.get_or_create(name='Operario')

    permisosOperario = Permission.objects.filter(
        codename__in=[
            'registrar_produccion',
            'editar_produccion',
            'actualizar_etapas_lote',
            'registrar_produccion'
        ]
    )
    

    operario.permissions.set(permisosOperario)

class Migration(migrations.Migration):

    dependencies = [
        ('bioKelpApp', '0003_especie_permiso_planta_and_more'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(crear_roles),
    ]