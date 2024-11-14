from django.db import connection
from horariosApp.models import Sala,DisponibilidadSala

def reset_sala_table():
    # Eliminar todos los registros en la tabla Seccion
    Sala.objects.all().delete()
    DisponibilidadSala.objects.all().delete()
    

    with connection.cursor() as cursor:
        cursor.execute("ALTER TABLE horariosapp_disponibilidadsala AUTO_INCREMENT = 1")
            # Reiniciar el contador de auto incremento
        cursor.execute("ALTER TABLE horariosapp_sala AUTO_INCREMENT = 1")

        
