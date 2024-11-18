from django.core.management.base import BaseCommand
from django.db.models import F, ExpressionWrapper, DecimalField
from horariosApp.models import Seccion, Sala, DisponibilidadSala, Bloque

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

            restriccion = []  # Lista para almacenar las salas que ya se han intentado

            while True:
                # Buscar una sala que tenga el cupo más cercano al número de alumnos, excluyendo las ya intentadas
                sala_candidata = (
                    Sala.objects
                    .filter(cupo_estandar__gte=cant_alumnos)  # Solo consideramos salas con cupo suficiente
                    .exclude(id__in=restriccion)  # Excluir salas en la lista de restricción
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

                if not sala_candidata:
                    self.stdout.write(f"No se encontró ninguna sala adecuada para la sección {seccion.asignatura}.")
                    break

                # Buscar los bloques disponibles para la sala actual, solo los que tengan 'disponible=True'
                bloques_disponibles = DisponibilidadSala.objects.filter(sala=sala_candidata, disponible=True).order_by('bloque').values_list('id', flat=True)
                bloques_disponible1 = list(bloques_disponibles)
                print(bloques_disponible1)

                if len(bloques_disponibles) >= cant_bloques:
                    self.stdout.write(f"La sala asignada es {sala_candidata.descripcion} con un cupo de {sala_candidata.cupo_estandar}.")
                    self.stdout.write(f"Hay suficientes bloques disponibles. Se asignarán {cant_bloques} bloques a la sección.")
                    
                    bloques_por_dia = { 
                        'lunes': [],
                        'martes': [],
                        'miercoles': [],
                        'jueves': [],
                        'viernes': [],

                    }

                    # Consultamos todos los bloques disponibles
                    bloques = Bloque.objects.all()

                    # Asignamos los bloques a cada día de la semana, guardando solo el id
                    for bloque in bloques:
                        # Agregar el id del bloque al día correspondiente
                        if bloque.dia in bloques_por_dia:
                            bloques_por_dia[bloque.dia].append(bloque.id)

                    # Mostramos los bloques disponibles por día
                    self.stdout.write(f"Bloques disponibles por día: {bloques_por_dia}")

                    # Asignación de bloques según la cantidad de bloques por semana
                    if cant_bloques == 3:
                        print('n/a')
                    elif cant_bloques == 4:

                        
                        # Filtrar las salas donde la disponibilidad es negativa (disponible=False)
                        disponibilidad_salas_no_disponibles = DisponibilidadSala.objects.filter(
                            disponible=0,  # Filtramos las salas que no están disponibles
                            sala_id=sala_candidata 
                        )
                        salas_no_disponibles_ids = [disponibilidad.bloque.id for disponibilidad in disponibilidad_salas_no_disponibles]

                        print(f'salas no disponibles{salas_no_disponibles_ids}')
                        print(f'sala selecionada{sala_candidata.descripcion}')
                        for dia, salas in bloques_por_dia.items():
                            bloques_por_dia[dia] = [sala_id for sala_id in salas if sala_id not in salas_no_disponibles_ids]
                        dias_disponibles = list(bloques_por_dia.keys())  # Lista de días disponibles en los bloques











                        # Asignar el primer día
                        dia_asignado_1 = None

                        # Verificar si hay bloques por día
                        for dia in dias_disponibles:
                            if bloques_por_dia.get(dia):  # Si hay bloques disponibles en ese día
                                dia_asignado_1 = dia  # Asignamos el primer día con bloques
                                break  # Terminamos el ciclo una vez asignado un día

                        # Si no se encuentra un día con bloques, asignar el siguiente día disponible
                        if dia_asignado_1 is None:
                            dia_asignado_1 = dias_disponibles[0]  # Si no hay bloques, asignamos el primer día disponible

                        # Asignar el día siguiente al día asignado 1 (día_asignado_2)
                        dia_asignado_2 = None
                        indice_dia_asignado_1 = dias_disponibles.index(dia_asignado_1)

                        # Buscar el siguiente día disponible
                        for i in range(indice_dia_asignado_1 + 1, len(dias_disponibles)):
                            if bloques_por_dia.get(dias_disponibles[i]):  # Verificar si hay bloques en el siguiente día
                                dia_asignado_2 = dias_disponibles[i]
                                break

                        # Si no se encuentra un día con bloques, asignar el siguiente disponible después del último
                        if dia_asignado_2 is None:
                            for dia in dias_disponibles:
                                if bloques_por_dia.get(dia):
                                    dia_asignado_2 = dia
                                    break

                        # Imprimir los días asignados
                        print("Día asignado 1:", dia_asignado_1)
                        print("Día asignado 2:", dia_asignado_2)






                        

                        # Inicializamos una lista para los bloques asignados
                        bloques_asignados = []
                        bloques_disponibles = bloques_por_dia[dia_asignado_1]
                        # Recorremos los bloques disponibles para buscar secuencias consecutivas
                        for i in range(len(bloques_disponibles) - 1):
                            if bloques_disponibles[i] + 1 == bloques_disponibles[i + 1]:
                                # Si encontramos bloques consecutivos, los asignamos
                                bloques_asignados = [bloques_disponibles[i], bloques_disponibles[i + 1]]
                                break

                        # Si no se encontró ninguna secuencia consecutiva
                        if not bloques_asignados:
                            bloques_asignados = f"No se pueden asignar bloques consecutivos para el día {dia_asignado_1}"
                        print(f"Bloques asignados para {dia_asignado_1}: {bloques_asignados}")





                         # Muestra los bloques asignados por día
                        self.stdout.write(f"BLOQUES ASIGNADOS:")
                        self.stdout.write(f"Dia: {dia_asignado_1} - Bloques: {bloques_asignados}")
                        self.stdout.write(f"Dia: {dia_asignado_2} - Bloques: ")




                    elif cant_bloques == 5:
                        print('n/a')
                    elif cant_bloques == 6:
                        print('n/a')
                    else:
                        self.stdout.write("La cantidad de bloques no está definida en las reglas establecidas.")
                        return
                    break
                else:
                    # Añadir la sala actual a la lista de restricciones para no volver a seleccionarla
                    restriccion.append(sala_candidata.id)
                    self.stdout.write(f"La sala {sala_candidata.descripcion} no tiene suficientes bloques disponibles. Intentando con otra sala...")
                    
        except Seccion.DoesNotExist:
            self.stdout.write("La sección no existe.")
