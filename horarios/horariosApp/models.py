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



