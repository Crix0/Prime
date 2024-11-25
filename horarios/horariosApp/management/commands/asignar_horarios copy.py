from django.core.management.base import BaseCommand
from django.db.models import F, ExpressionWrapper, DecimalField
from horariosApp.models import Seccion, Sala, DisponibilidadSala, Bloque, Horario

class Command(BaseCommand):
    help = 'Asigna un horario a una sección predeterminada'

    def handle(self, *args, **kwargs):
        try:
            # Obtener la sección por ID (sección específica, por ejemplo, id=1)
            seccion_id = 10 # Cambia esto por el ID que desees
            seccion = Seccion.objects.get(id=seccion_id)
            
            # Extraer la cantidad de alumnos de la sección
            cant_alumnos = seccion.cant_alumnos
            cant_bloques = seccion.cant_bloques  # Obtener la cantidad de bloques necesarios
            print(f"La cantidad de alumnos en la sección {seccion.asignatura} es: {cant_alumnos}")
            print(f"La cantidad de bloques necesarios para la sección es: {cant_bloques}")

            restriccion = []  # Lista para almacenar las salas que ya se han intentado
            dias_restringidos = []
            

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
                    print(f"No se encontró ninguna sala adecuada para la sección {seccion.asignatura}.")
                    break

                
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




                #VERIFIJA SI ES DIURNA O VERPERTINA Y FILTRA LOS BLOQUES
                if seccion.jornada == "DIURNA"  :
                    bloques_vespertinos = {bloque.id for bloque in bloques if bloque.tipo == "vespertino"}
                    # Eliminamos los bloques "vespertinos" de bloques_por_dia
                    for dia, ids in bloques_por_dia.items():
                        bloques_por_dia[dia] = [bloque_id for bloque_id in ids if bloque_id not in bloques_vespertinos]
                else:
                    bloques_vespertinos = {bloque.id for bloque in bloques if bloque.tipo == "diurno"}
                    # Eliminamos los bloques "vespertinos" de bloques_por_dia
                    for dia, ids in bloques_por_dia.items():
                        bloques_por_dia[dia] = [bloque_id for bloque_id in ids if bloque_id not in bloques_vespertinos]
                
                

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

                print(bloques_por_dia)
                        
                
            

                # Asignación de bloques según la cantidad de bloques por semana
                if cant_bloques == 3:

                    dias_disponibles_validos = [dia for dia in dias_disponibles if dia not in dias_restringidos]

                    # Si no hay días válidos, no se puede asignar
                    if not dias_disponibles_validos:
                        print("No hay más días disponibles para asignar.")
                        restriccion.append(sala_candidata.id)
                        continue

                    # Intentar asignar un día
                    dia_asignado_1 = None
                    for dia in dias_disponibles_validos:
                        bloques = bloques_por_dia.get(dia, [])
                        if len(bloques) > 2:  # Si hay más de 2 bloques disponibles
                            dia_asignado_1 = dia
                            break

                    # Si no se encuentra un día con bloques suficientes, terminamos
                    if dia_asignado_1 is None:
                        print("No se encontró un día con suficientes bloques.")
                        restriccion.append(sala_candidata.id)
                        continue

                    # Intentar asignar bloques consecutivos
                    bloques_asignados_1 = []
                    bloques_disponibles = bloques_por_dia[dia_asignado_1]

                    for i in range(len(bloques_disponibles) - 2):  # Cambiamos el rango para evitar desbordes
                        if (bloques_disponibles[i] + 1 == bloques_disponibles[i + 1] and 
                            bloques_disponibles[i + 1] + 1 == bloques_disponibles[i + 2]):
                            # Si encontramos 3 bloques consecutivos, los asignamos
                            bloques_asignados_1 = [bloques_disponibles[i], bloques_disponibles[i + 1], bloques_disponibles[i + 2]]
                            break

                    if not bloques_asignados_1:
                        print(f"No se pueden asignar bloques consecutivos para el día {dia_asignado_1}")
                        dias_restringidos.append(dia_asignado_1)
                        continue
                    else:
                        print(f"Bloques asignados para {dia_asignado_1}: {bloques_asignados_1}")


                    bloque_asignados = bloques_asignados_1





                    #ASIGNACION A  BASEDEDTOS HORARIOS
                    print(sala_candidata)
                    print(bloque_asignados)
                    
                    ids = DisponibilidadSala.objects.filter(
                        sala_id=sala_candidata,
                        bloque_id__in=bloque_asignados
                    ).values_list('id', flat=True)

                    # Imprimir los IDs
                    print(list(ids))



                    DisponibilidadSala.objects.filter(
                        sala_id=sala_candidata,
                        bloque_id__in=bloque_asignados
                    ).update(disponible=0)

                    # Obtener la sección correspondiente
                    seccion_asignada = Seccion.objects.get(id=seccion_id)  # Reemplaza `seccion_id` con el ID de la sección

                    # Crear registros en la tabla `Horario` evitando duplicados
                    disponibilidades = DisponibilidadSala.objects.filter(
                        sala_id=sala_candidata,
                        bloque_id__in=bloque_asignados
                    )

                    for disponibilidad in disponibilidades:
                        # Verificar que no exista ya la combinación para evitar duplicados
                        if not Horario.objects.filter(seccion=seccion_asignada, disponibilidad_sala=disponibilidad).exists():
                            Horario.objects.create(
                                seccion=seccion_asignada,
                                disponibilidad_sala=disponibilidad
                            )
                    break

                elif cant_bloques == 4:

                    
                    


                    dias_disponibles_validos = [dia for dia in dias_disponibles if dia not in dias_restringidos]

                    # Si no hay días válidos, no se puede asignar
                    if not dias_disponibles_validos:
                        print("No hay más días disponibles para asignar.")
                        restriccion.append(sala_candidata.id)
                        continue

                    # Intentar asignar un día
                    dia_asignado_1 = None
                    for dia in dias_disponibles_validos:
                        bloques = bloques_por_dia.get(dia, [])
                        if len(bloques) > 1:  # Si hay más de 1 bloques disponibles
                            dia_asignado_1 = dia
                            break


                    if len(bloques) == 3:  # Si hay más de 2 bloques disponibles
                        dias_restringidos.append(dia_asignado_1)
                        continue


                    # Si no se encuentra un día con bloques suficientes, terminamos
                    if dia_asignado_1 is None:
                        print("No se encontró un día con suficientes bloques.")
                        restriccion.append(sala_candidata.id)
                        continue
                    
                    dia_asignado_2 = None
                    for dia in dias_disponibles_validos:
                        if dia == dia_asignado_1 or dia in dias_restringidos:  # Excluir el día ya asignado y restringidos
                            continue
                        bloques = bloques_por_dia.get(dia, [])
                        if len(bloques) > 1:  # Si hay más de 2 bloques disponibles
                            dia_asignado_2 = dia
                            break

                    if len(bloques) == 3:  # Si hay más de 2 bloques disponibles
                        dias_restringidos.append(dia_asignado_2)
                        continue

                    if dia_asignado_2 is None:
                        print("No se encontró un segundo día con suficientes bloques.")
                        restriccion.append(sala_candidata.id)
                        continue






                    #  asignar bloques consecutivos
                    bloques_asignados_1 = []
                    bloques_disponibles = bloques_por_dia[dia_asignado_1]

                    for i in range(len(bloques_disponibles) - 1):
                        if bloques_disponibles[i] + 1 == bloques_disponibles[i + 1]:
                            # Si encontramos bloques consecutivos, los asignamos
                            bloques_asignados_1 = [bloques_disponibles[i], bloques_disponibles[i + 1]]
                            break

                    bloques_asignados_2 = []
                    bloques_disponibles = bloques_por_dia[dia_asignado_2]
                    # Recorremos los bloques disponibles para buscar secuencias consecutivas
                    for i in range(len(bloques_disponibles) - 1):
                        if bloques_disponibles[i] + 1 == bloques_disponibles[i + 1]:
                            # Si encontramos bloques consecutivos, los asignamos
                            bloques_asignados_2 = [bloques_disponibles[i], bloques_disponibles[i + 1]]
                            break

                    if not bloques_asignados_1:
                        print(f"No se pueden asignar bloques consecutivos para el día {dia_asignado_1}")
                        dias_restringidos.append(dia_asignado_1)
                        continue
                    if not bloques_asignados_2:
                        print(f"No se pueden asignar bloques consecutivos para el día {dia_asignado_2}")
                        dias_restringidos.append(dia_asignado_2)
                        continue
                    else:
                        print(f"Bloques asignados para {dia_asignado_1}: {bloques_asignados_1}")
                        print(f"Bloques asignados para {dia_asignado_2}: {bloques_asignados_2}")
                        
                    

                    bloque_asignados = bloques_asignados_1 + bloques_asignados_2





                    #ASIGNACION A  BASEDEDTOS HORARIOS
                    print(sala_candidata)
                    print(bloque_asignados)
                    
                    ids = DisponibilidadSala.objects.filter(
                        sala_id=sala_candidata,
                        bloque_id__in=bloque_asignados
                    ).values_list('id', flat=True)

                    # Imprimir los IDs
                    print(list(ids))



                    DisponibilidadSala.objects.filter(
                        sala_id=sala_candidata,
                        bloque_id__in=bloque_asignados
                    ).update(disponible=0)

                    # Obtener la sección correspondiente
                    seccion_asignada = Seccion.objects.get(id=seccion_id)  # Reemplaza `seccion_id` con el ID de la sección

                    # Crear registros en la tabla `Horario` evitando duplicados
                    disponibilidades = DisponibilidadSala.objects.filter(
                        sala_id=sala_candidata,
                        bloque_id__in=bloque_asignados
                    )

                    for disponibilidad in disponibilidades:
                        # Verificar que no exista ya la combinación para evitar duplicados
                        if not Horario.objects.filter(seccion=seccion_asignada, disponibilidad_sala=disponibilidad).exists():
                            Horario.objects.create(
                                seccion=seccion_asignada,
                                disponibilidad_sala=disponibilidad
                            )
                    break

                elif cant_bloques == 5:
                   
                    dias_disponibles_validos = [dia for dia in dias_disponibles if dia not in dias_restringidos]

                    # Si no hay días válidos, no se puede asignar
                    if not dias_disponibles_validos:
                        print("No hay más días disponibles para asignar.")
                        restriccion.append(sala_candidata.id)
                        continue

                    # Intentar asignar un día
                    dia_asignado_1 = None
                    for dia in dias_disponibles_validos:
                        bloques = bloques_por_dia.get(dia, [])
                        if len(bloques) > 2:  # Si hay más de 2 bloques disponibles
                            dia_asignado_1 = dia
                            break

                    # Si no se encuentra un día con bloques suficientes, terminamos
                    if dia_asignado_1 is None:
                        # FUTURA ACTUALIZACION PIBARDOS
                        # FUTURA ACTUALIZACION PIBARDOS
                        # FUTURA ACTUALIZACION PIBARDOS
                        # FUTURA ACTUALIZACION PIBARDOS
                        # FUTURA ACTUALIZACION PIBARDOS
                        # FUTURA ACTUALIZACION PIBARDOS
                        # FUTURA ACTUALIZACION PIBARDOS
                        # FUTURA ACTUALIZACION PIBARDOS
                        # FUTURA ACTUALIZACION PIBARDOS
                        
                        print("No se encontró un día con suficientes bloques.")
                        restriccion.append(sala_candidata.id)
                        continue


                    dia_asignado_2 = None
                    for dia in dias_disponibles_validos:
                        if dia == dia_asignado_1 or dia in dias_restringidos:  # Excluir el día ya asignado y restringidos
                            continue
                        bloques = bloques_por_dia.get(dia, [])
                        if len(bloques) > 1:  # Si hay más de 2 bloques disponibles
                            dia_asignado_2 = dia
                            break

                    

                    if dia_asignado_2 is None:
                        print("No se encontró un segundo día con suficientes bloques.")
                        restriccion.append(sala_candidata.id)
                        continue



                    # Intentar asignar bloques consecutivos
                    bloques_asignados_1 = []
                    bloques_disponibles = bloques_por_dia[dia_asignado_1]

                    for i in range(len(bloques_disponibles) - 2):  # Cambiamos el rango para evitar desbordes
                        if (bloques_disponibles[i] + 1 == bloques_disponibles[i + 1] and 
                            bloques_disponibles[i + 1] + 1 == bloques_disponibles[i + 2]):
                            # Si encontramos 3 bloques consecutivos, los asignamos
                            bloques_asignados_1 = [bloques_disponibles[i], bloques_disponibles[i + 1], bloques_disponibles[i + 2]]
                            break

                    bloques_asignados_2 = []
                    bloques_disponibles = bloques_por_dia[dia_asignado_2]
                    # Recorremos los bloques disponibles para buscar secuencias consecutivas
                    for i in range(len(bloques_disponibles) - 1):
                        if bloques_disponibles[i] + 1 == bloques_disponibles[i + 1]:
                            # Si encontramos bloques consecutivos, los asignamos
                            bloques_asignados_2 = [bloques_disponibles[i], bloques_disponibles[i + 1]]
                            break

                    if not bloques_asignados_1:
                        print(f"No se pueden asignar bloques consecutivos para el día {dia_asignado_1}")
                        dias_restringidos.append(dia_asignado_1)
                        continue
                    if not bloques_asignados_2:
                        print(f"No se pueden asignar bloques consecutivos para el día {dia_asignado_2}")
                        dias_restringidos.append(dia_asignado_2)
                        continue
                    else:
                        print(f"Bloques asignados para {dia_asignado_1}: {bloques_asignados_1}")
                        print(f"Bloques asignados para {dia_asignado_2}: {bloques_asignados_2}")


                    bloque_asignados = bloques_asignados_1 + bloques_asignados_2





                    #ASIGNACION A  BASEDEDTOS HORARIOS
                    print(sala_candidata)
                    print(bloque_asignados)
                    
                    ids = DisponibilidadSala.objects.filter(
                        sala_id=sala_candidata,
                        bloque_id__in=bloque_asignados
                    ).values_list('id', flat=True)

                    # Imprimir los IDs
                    print(list(ids))



                    DisponibilidadSala.objects.filter(
                        sala_id=sala_candidata,
                        bloque_id__in=bloque_asignados
                    ).update(disponible=0)

                    # Obtener la sección correspondiente
                    seccion_asignada = Seccion.objects.get(id=seccion_id)  # Reemplaza `seccion_id` con el ID de la sección

                    # Crear registros en la tabla `Horario` evitando duplicados
                    disponibilidades = DisponibilidadSala.objects.filter(
                        sala_id=sala_candidata,
                        bloque_id__in=bloque_asignados
                    )

                    for disponibilidad in disponibilidades:
                        # Verificar que no exista ya la combinación para evitar duplicados
                        if not Horario.objects.filter(seccion=seccion_asignada, disponibilidad_sala=disponibilidad).exists():
                            Horario.objects.create(
                                seccion=seccion_asignada,
                                disponibilidad_sala=disponibilidad
                            )
                    break

                elif cant_bloques == 6:


                    dias_disponibles_validos = [dia for dia in dias_disponibles if dia not in dias_restringidos]

                    # Si no hay días válidos, no se puede asignar
                    if not dias_disponibles_validos:
                        print("No hay más días disponibles para asignar.")
                        restriccion.append(sala_candidata.id)
                        continue

                    # Intentar asignar un día
                    dia_asignado_1 = None
                    for dia in dias_disponibles_validos:
                        bloques = bloques_por_dia.get(dia, [])
                        if len(bloques) > 1:  # Si hay más de 1 bloques disponibles
                            dia_asignado_1 = dia
                            break

                    # Si no se encuentra un día con bloques suficientes, terminamos
                    if dia_asignado_1 is None:
                        print("No se encontró un día con suficientes bloques.")
                        restriccion.append(sala_candidata.id)
                        continue
                    
                    dia_asignado_2 = None
                    for dia in dias_disponibles_validos:
                        if dia == dia_asignado_1 or dia in dias_restringidos:  # Excluir el día ya asignado y restringidos
                            continue
                        bloques = bloques_por_dia.get(dia, [])
                        if len(bloques) > 1:  # Si hay más de 2 bloques disponibles
                            dia_asignado_2 = dia
                            break

                    if dia_asignado_2 is None:
                        print("No se encontró un segundo día con suficientes bloques.")
                        restriccion.append(sala_candidata.id)
                        continue

                    dia_asignado_3 = None
                    for dia in dias_disponibles_validos:
                        if dia in [dia_asignado_1, dia_asignado_2] or dia in dias_restringidos:  # Excluir días ya asignados y restringidos
                            continue
                        bloques = bloques_por_dia.get(dia, [])
                        if len(bloques) > 1:  # Si hay más de 1 bloques disponibles
                            dia_asignado_3 = dia
                            break

                    if dia_asignado_3 is None:
                        print("No se encontró un tercer día con suficientes bloques.")
                        restriccion.append(sala_candidata.id)
                        continue








                    

                    #  asignar bloques consecutivos
                    bloques_asignados_1 = []
                    bloques_disponibles = bloques_por_dia[dia_asignado_1]

                    for i in range(len(bloques_disponibles) - 1):
                        if bloques_disponibles[i] + 1 == bloques_disponibles[i + 1]:
                            # Si encontramos bloques consecutivos, los asignamos
                            bloques_asignados_1 = [bloques_disponibles[i], bloques_disponibles[i + 1]]
                            break

                    bloques_asignados_2 = []
                    bloques_disponibles = bloques_por_dia[dia_asignado_2]
                    # Recorremos los bloques disponibles para buscar secuencias consecutivas
                    for i in range(len(bloques_disponibles) - 1):
                        if bloques_disponibles[i] + 1 == bloques_disponibles[i + 1]:
                            # Si encontramos bloques consecutivos, los asignamos
                            bloques_asignados_2 = [bloques_disponibles[i], bloques_disponibles[i + 1]]
                            break

                    bloques_asignados_3 = []
                    bloques_disponibles = bloques_por_dia[dia_asignado_3]
                    # Recorremos los bloques disponibles para buscar secuencias consecutivas
                    for i in range(len(bloques_disponibles) - 1):
                        if bloques_disponibles[i] + 1 == bloques_disponibles[i + 1]:
                            # Si encontramos bloques consecutivos, los asignamos
                            bloques_asignados_3 = [bloques_disponibles[i], bloques_disponibles[i + 1]]
                            break

                    if not bloques_asignados_1:
                        print(f"No se pueden asignar bloques consecutivos para el día {dia_asignado_1}")
                        dias_restringidos.append(dia_asignado_1)
                        continue
                    if not bloques_asignados_2:
                        print(f"No se pueden asignar bloques consecutivos para el día {dia_asignado_2}")
                        dias_restringidos.append(dia_asignado_2)
                        continue
                    if not bloques_asignados_3:
                        print(f"No se pueden asignar bloques consecutivos para el día {dia_asignado_3}")
                        dias_restringidos.append(dia_asignado_3)
                        continue
                    else:
                        print(f"Bloques asignados para {dia_asignado_1}: {bloques_asignados_1}")
                        print(f"Bloques asignados para {dia_asignado_2}: {bloques_asignados_2}")
                        print(f"Bloques asignados para {dia_asignado_3}: {bloques_asignados_3}")




                    bloque_asignados = bloques_asignados_1 + bloques_asignados_2 + bloques_asignados_3
                    #ASIGNACION A  BASEDEDTOS HORARIOS
                    print(sala_candidata)
                    print(bloque_asignados)
                    
                    ids = DisponibilidadSala.objects.filter(
                        sala_id=sala_candidata,
                        bloque_id__in=bloque_asignados
                    ).values_list('id', flat=True)

                    # Imprimir los IDs
                    print(list(ids))



                    DisponibilidadSala.objects.filter(
                        sala_id=sala_candidata,
                        bloque_id__in=bloque_asignados
                    ).update(disponible=0)

                    # Obtener la sección correspondiente
                    seccion_asignada = Seccion.objects.get(id=seccion_id)  # Reemplaza `seccion_id` con el ID de la sección

                    # Crear registros en la tabla `Horario` evitando duplicados
                    disponibilidades = DisponibilidadSala.objects.filter(
                        sala_id=sala_candidata,
                        bloque_id__in=bloque_asignados
                    )

                    for disponibilidad in disponibilidades:
                        # Verificar que no exista ya la combinación para evitar duplicados
                        if not Horario.objects.filter(seccion=seccion_asignada, disponibilidad_sala=disponibilidad).exists():
                            Horario.objects.create(
                                seccion=seccion_asignada,
                                disponibilidad_sala=disponibilidad
                            )
                    break

                else:
                    print("La cantidad de bloques no está definida en las reglas establecidas.")
                    return           
        except Seccion.DoesNotExist:
            print("La sección no existe.")

