from django.core.management.base import BaseCommand
from django.db.models import F, ExpressionWrapper, DecimalField
from horariosApp.models import Seccion, Sala, DisponibilidadSala

class Command(BaseCommand):
    help = 'Asigna un horario a una sección predeterminada'

    def handle(self, *args, **kwargs):
        try:
            # Obtener la sección por ID (sección específica, por ejemplo, id=1)
            seccion_id = 1  # Cambia esto por el ID que desees
            seccion = Seccion.objects.get(id=seccion_id)
            
            # Extraer la cantidad de alumnos de la sección
            cant_alumnos = seccion.cant_alumnos
            cant_bloques = seccion.cant_bloques  # Obtener la cantidad de bloques necesarios
            self.stdout.write(f"La cantidad de alumnos en la sección {seccion.asignatura} es: {cant_alumnos}")
            self.stdout.write(f"La cantidad de bloques necesarios para la sección es: {cant_bloques}")
            
            # Buscar una sala que tenga el cupo más cercano al número de alumnos
            sala_candidata = (
                Sala.objects
                .filter(cupo_estandar__gte=cant_alumnos)  # Solo consideramos salas con cupo suficiente
                .annotate(diferencia=ExpressionWrapper(
                    F('cupo_estandar') - cant_alumnos, 
                    output_field=DecimalField()
                ))  # Calculamos la diferencia de cupo
                .annotate(diferencia_abs=ExpressionWrapper(
                    F('diferencia'),  # Aplica abs() para obtener la diferencia absoluta
                    output_field=DecimalField()
                ))
                .order_by('diferencia_abs')  # Ordenamos por la diferencia absoluta más pequeña
                .first()  # Tomamos la primera sala que tenga la menor diferencia
            )
            
            if sala_candidata:
                self.stdout.write(f"La sala asignada es {sala_candidata.descripcion} con un cupo de {sala_candidata.cupo_estandar}.")
                
                # Buscar los bloques disponibles para la sala, solo los que tengan 'disponible=True'
                bloques_disponibles = DisponibilidadSala.objects.filter(sala=sala_candidata,disponible=True).order_by('bloque').values_list('id', flat=True)
                if len(bloques_disponibles) >= cant_bloques:
                    self.stdout.write(f"Hay suficientes bloques disponibles. Se asignarán{bloques_disponibles} {cant_bloques} bloques a la sección.")
                    
                    # Aquí puedes asignar los bloques a la sección, por ejemplo:
                    # for bloque_id in bloques_disponibles:
                    #     # Asignar el bloque a la sección
                    #     seccion.bloques.add(bloque_id)  # Suponiendo que hay una relación ManyToMany entre Seccion y DisponibilidadSala
                    
                    # Si deseas asignar el horario de forma específica (fecha y hora), puedes hacerlo aquí
                    
                else:
                    self.stdout.write(f"No hay suficientes bloques disponibles para la sección {seccion.asignatura}.")
                    # futuro while con limitdor para usar esa sala
            else:
                self.stdout.write(f"No se encontró una sala adecuada para la sección {seccion.asignatura}.")
                
        except Seccion.DoesNotExist:
            self.stdout.write("La sección no existe.")
