from horariosApp.models import Sala, Bloque, DisponibilidadSala

def rellenar():
    salas = Sala.objects.all()  # Obtiene todas las salas
    bloques = Bloque.objects.all()  # Obtiene todos los bloques

    for sala in salas:
        for bloque in bloques:
            DisponibilidadSala.objects.get_or_create(
                sala=sala,
                bloque=bloque,
                defaults={'disponible': True}  # Todas las salas están disponibles inicialmente
            )
