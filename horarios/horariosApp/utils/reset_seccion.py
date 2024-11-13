from django.db import connection
from horariosApp.models import Seccion

def reset_seccion_table():
    # Eliminar todos los registros en la tabla Seccion
    Seccion.objects.all().delete()
    
    # Reiniciar el contador de auto incremento
    with connection.cursor() as cursor:
        cursor.execute("ALTER TABLE horariosapp_seccion AUTO_INCREMENT = 1")
