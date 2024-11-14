from horariosApp.models import Seccion, Sala, DisponibilidadSala, Horario
from django.db.models import F, ExpressionWrapper, DecimalField

def asignar_horario_a_seccion(seccion_id):
    try:
        # Obtener la sección por ID
        seccion = Seccion.objects.get(id=seccion_id)

        cant_alumnos = seccion.cant_alumnos
        print(f"La cantidad de alumnos en la sección {seccion.asignatura} es: {cant_alumnos}")
        

        sala_candidata = (
            Sala.objects
            .annotate(diferencia=ExpressionWrapper(
                abs(F('cupo_estandar') - cant_alumnos), 
                output_field=DecimalField()
            ))  # Cálculo de la diferencia de cupo
            .order_by('diferencia')  # Ordenamos para obtener la sala con el cupo más cercano
            .first()
        )
        
        if sala_candidata:
            print(f"La sala asignada es {sala_candidata.descripcion} con un cupo de {sala_candidata.cupo_estandar}.")
        else:
            print(f"No se encontró una sala adecuada para la sección {seccion.asignatura}.")


        
        
    
    except Seccion.DoesNotExist:
        print("La sección no existe.")

    except Exception as e:
        print(f"Ocurrió un error: {e}")

def asignar_horarios():
    secciones = Seccion.objects.all()  # Obtén todas las secciones

    for seccion in secciones:
        asignar_horario_a_seccion(seccion.id)  # Llama a la función para cada sección

