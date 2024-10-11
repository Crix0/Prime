from django.core.management.base import BaseCommand
from horariosApp.models import Sala, Bloque, DisponibilidadSala



def rellenar_disponibilidad():
    salas = Sala.objects.all()  # Obtiene todas las salas
    bloques = Bloque.objects.all()  # Obtiene todos los bloques

    for sala in salas:
        for bloque in bloques:
            DisponibilidadSala.objects.get_or_create(
                sala=sala,
                bloque=bloque,
                defaults={'disponible': True}  # Todas las salas están disponibles inicialmente
            )

class Command(BaseCommand):
    help = 'Rellena la tabla de disponibilidad con bloques y salas'

    def handle(self, *args, **kwargs):


        # Rellenar disponibilidad
        rellenar_disponibilidad()

        self.stdout.write(self.style.SUCCESS('Tabla de disponibilidad rellenada correctamente.'))

