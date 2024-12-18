from django.db import models

class Seccion(models.Model):
    programa_estudio = models.CharField(max_length=100)
    mencion = models.CharField(max_length=100)
    plan = models.CharField(max_length=100)
    semestre = models.IntegerField()
    cod_asignatura = models.CharField(max_length=10)
    asignatura = models.CharField(max_length=100)
    hrs_asignatura = models.IntegerField()
    seccion = models.CharField(max_length=10)
    cant_bloques = models.IntegerField(default=0)
    jornada = models.CharField(max_length=50)
    cupo = models.IntegerField()
    cant_alumnos = models.IntegerField()
    modalidad = models.CharField(max_length=50)
    subseccion = models.CharField(max_length=50)
    tipo_subseccion = models.CharField(max_length=50)
    alumnos_cft = models.IntegerField()
    alumnos_ip = models.IntegerField()
    alumnos_utc = models.IntegerField()
    estado_seccion = models.CharField(max_length=50)
    horas_plan_seccion_subseccion = models.IntegerField()
    hrs_planificadas = models.IntegerField()
    fecha_inicio = models.DateField()
    fecha_termino = models.DateField()
    

class Sala(models.Model):
    codigo_iso = models.CharField(max_length=10)
    tipo_sala = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=255)
    sup_m2 = models.DecimalField(max_digits=5, decimal_places=2)
    ubicacion = models.CharField(max_length=100)
    cupo_estandar = models.IntegerField()


class Bloque(models.Model):
    DIA_SEMANA_CHOICES = [
        ('lunes', 'Lunes'),
        ('martes', 'Martes'),
        ('miércoles', 'Miércoles'),
        ('jueves', 'Jueves'),
        ('viernes', 'Viernes'),
    ]
    
    TIPO_BLOQUE_CHOICES = [
        ('diurno', 'Diurno'),
        ('vespertino', 'Vespertino'),
    ]
    
    dia = models.CharField(max_length=10, choices=DIA_SEMANA_CHOICES)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    tipo = models.CharField(max_length=10, choices=TIPO_BLOQUE_CHOICES)

    def __str__(self):
        return f"{self.dia}: {self.hora_inicio} - {self.hora_fin} ({self.tipo})"

class DisponibilidadSala(models.Model):
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE)
    bloque = models.ForeignKey(Bloque, on_delete=models.CASCADE)
    disponible = models.BooleanField(default=True)  # True si la sala está disponible en ese bloque

    class Meta:
        unique_together = ('sala', 'bloque')  # Evitar duplicados de disponibilidad

    def __str__(self):
        estado = "Disponible" if self.disponible else "No disponible"
        return f"{self.sala.descripcion} - {self.bloque} : {estado}"

class Horario(models.Model):
    seccion = models.ForeignKey(Seccion, on_delete=models.CASCADE)
    disponibilidad_sala = models.ForeignKey(DisponibilidadSala, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('seccion', 'disponibilidad_sala')  # Evitar duplicados de asignación

    def __str__(self):
        return f"Sección: {self.seccion.asignatura} ({self.seccion.seccion}) - Sala: {self.disponibilidad_sala.sala}"


class VistaHorario(models.Model):
    horario_id = models.IntegerField()
    cod_asignatura = models.CharField(max_length=10)
    asignatura = models.CharField(max_length=100)
    hrs_asignatura = models.IntegerField()
    seccion = models.CharField(max_length=10)
    cant_bloques = models.IntegerField()
    sala_codigo_iso = models.CharField(max_length=10)
    tipo_sala = models.CharField(max_length=100)
    sala_disponible = models.BooleanField()
    bloque_dia = models.CharField(max_length=10)
    bloque_hora_inicio = models.TimeField()
    bloque_hora_fin = models.TimeField()
    bloque_tipo = models.CharField(max_length=10)

    class Meta:
        managed = False  # No gestionado por Django, ya que es una vista
        db_table = "vista_horarios"  # Nombre exacto de la vista en la base de datos