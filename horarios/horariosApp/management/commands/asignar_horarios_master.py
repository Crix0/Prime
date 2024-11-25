from django.core.management.base import BaseCommand
from horariosApp.models import Seccion
from horariosApp.management.commands.asignar_horarios import asignar

class Command(BaseCommand):
    help = 'Asigna un horario a una sección predeterminada'

    def handle(self, *args, **kwargs):
        # Filtrar y ordenar las secciones según la cantidad de bloques y luego por 'cant_alumnos'
        bloques3_ids = Seccion.objects.filter(cant_bloques=3).order_by('-cant_alumnos').values_list('id', flat=True)
        bloques4_ids = Seccion.objects.filter(cant_bloques=4).order_by('-cant_alumnos').values_list('id', flat=True)
        bloques5_ids = Seccion.objects.filter(cant_bloques=5).order_by('-cant_alumnos').values_list('id', flat=True)
        bloques6_ids = Seccion.objects.filter(cant_bloques=6).order_by('-cant_alumnos').values_list('id', flat=True)

        # Asignar los horarios 1 por 1 comenzando con los bloques de 6, luego 5, 4 y 3
        for seccion_id in bloques6_ids:
            # Llamamos a la función 'asignar' con el ID de la sección
            asignar(seccion_id)
            self.stdout.write(f"Asignado horario para sección ID: {seccion_id} en bloques 6")

        for seccion_id in bloques5_ids:
            # Llamamos a la función 'asignar' con el ID de la sección
            asignar(seccion_id)
            self.stdout.write(f"Asignado horario para sección ID: {seccion_id} en bloques 5")

        for seccion_id in bloques4_ids:
            # Llamamos a la función 'asignar' con el ID de la sección
            asignar(seccion_id)
            self.stdout.write(f"Asignado horario para sección ID: {seccion_id} en bloques 4")

        for seccion_id in bloques3_ids:
            # Llamamos a la función 'asignar' con el ID de la sección
            asignar(seccion_id)
            self.stdout.write(f"Asignado horario para sección ID: {seccion_id} en bloques 3")
