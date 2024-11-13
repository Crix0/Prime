from django.db import connection
from horariosApp.models import Sala,DisponibilidadSala

def reset_sala_table():
    # Eliminar todos los registros en la tabla Seccion
    Sala.objects.all().delete()
    
    # Reiniciar el contador de auto incremento
    with connection.cursor() as cursor:
        cursor.execute("ALTER TABLE horariosapp_sala AUTO_INCREMENT = 1")
        
