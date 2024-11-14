# planificar_bloques.py

from horariosApp.models import Seccion

def calcular_bloques(hrs_asignatura):
    """
    Calcula la cantidad de bloques en función de las horas de la asignatura.
    """
    if hrs_asignatura == 54:
        return 3
    elif hrs_asignatura == 72:
        return 4
    elif hrs_asignatura == 90:
        return 5
    elif hrs_asignatura == 108:
        return 6
    else:
        return 0  # Caso por defecto si las horas no coinciden con ningún valor

def asignar_bloques():
    """
    Recorre todas las secciones y asigna la cantidad de bloques correspondiente 
    a cada sección en función de las horas de la asignatura.
    """
    secciones = Seccion.objects.all()
    
    for seccion in secciones:
        cant_bloques = calcular_bloques(seccion.hrs_asignatura)
        
        # Actualiza la cantidad de bloques para la sección
        seccion.cant_bloques = cant_bloques
        seccion.save()

    print("Bloques asignados correctamente a todas las secciones.")
