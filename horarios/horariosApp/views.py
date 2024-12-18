from django.db import connection
from django.shortcuts import render, redirect, get_object_or_404
from .models import Seccion, Sala, Bloque, VistaHorario

from .forms import SeccionForm, SalaForm


from django.http import HttpResponse

from .utils.reset_sala import reset_sala_table
from .utils.reset_seccion import reset_seccion_table
from .utils.generador_bloque import asignar_bloques
from .utils.rellenar_disponibilidad import rellenar
from .utils.prueba import asignar_horario_a_seccion



import pandas as pd
# Create your views here.
def inicio(request):
    return render(request,'index.html')


# Vista Bloque
def horarios_view(request):
    bloques = Bloque.objects.all().order_by('hora_inicio')
    
    # Obtener los bloques únicos (puedes también usar `distinct()`)
    horarios_unicos = bloques.values_list('hora_inicio', 'hora_fin').distinct()
    
    dias = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes']
    horario = {dia: [] for dia in dias}

    for bloque in bloques:
        horario[bloque.dia].append(bloque)

    return render(request, 'horarios/horario.html', {'horario': horario, 'horarios_unicos': horarios_unicos})


def mostrar_horarios(request):
    # Obtener todos los registros de la vista
    horarios = VistaHorario.objects.all()

    # Organizar por día para facilitar la visualización
    horarios_por_dia = {
        "lunes": [],
        "martes": [],
        "miércoles": [],
        "jueves": [],
        "viernes": [],
    }

    for horario in horarios:
        if horario.bloque_dia in horarios_por_dia:
            horarios_por_dia[horario.bloque_dia].append(horario)

    return render(request, "horarios/horario.html", {"horarios_por_dia": horarios_por_dia})




# CRUD para Secciones
def listar_secciones(request):
    secciones = Seccion.objects.all()
    return render(request, 'secciones/listar_secciones.html', {
        'secciones': secciones,
        'current_section': 'secciones',
        'active_page': 'listar_secciones',
    })



def crear_secciones(request):
    if request.method == 'POST':
        form = SeccionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_secciones')
    else:
        form = SeccionForm()
    return render(request, 'secciones/crear_secciones.html', {
        'form': form,
        'current_section': 'secciones',
        'active_page': 'crear_secciones',
    })


def editar_secciones(request, id):
    seccion = get_object_or_404(Seccion, id=id)
    if request.method == 'POST':
        form = SeccionForm(request.POST, instance=seccion)
        if form.is_valid():
            form.save()
            return redirect('listar_secciones')
    else:
        form = SeccionForm(instance=seccion)
    return render(request, 'secciones/editar_secciones.html', {'form': form})

def eliminar_secciones(request, id):
    seccion = get_object_or_404(Seccion, id=id)
    if request.method == 'POST':
        seccion.delete()
        return redirect('listar_secciones')
    return render(request, 'secciones/eliminar_secciones.html', {'seccion': seccion})

# 
# 
# 
# 


# CRUD para Salas

def listar_salas(request):
    salas = Sala.objects.all()
    return render(request, 'salas/listar_salas.html', {
        'salas': salas,
        'current_section': 'salas',
        'active_page': 'listar_salas',
    })

def crear_salas(request):
    if request.method == 'POST':
        form = SalaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_salas')
    else:
        form = SalaForm()
    return render(request, 'salas/crear_salas.html', {
        'form': form,
        'current_section': 'salas',
        'active_page': 'crear_salas',
    })



def editar_salas(request, id):
    sala = get_object_or_404(Sala, id=id)
    if request.method == 'POST':
        form = SalaForm(request.POST, instance=sala)
        if form.is_valid():
            form.save()
            return redirect('listar_salas')
    else:
        form = SalaForm(instance=sala)
    return render(request, 'salas/editar_salas.html', {'form': form})

def eliminar_salas(request, id):
    sala = get_object_or_404(Sala, id=id)
    if request.method == 'POST':
        sala.delete()
        return redirect('listar_salas')
    return render(request, 'salas/eliminar_salas.html', {'sala': sala})



# 
# 
# 
# 

# IMPORTAR SECCIONES//SALAS
def importar_secciones(request):
    if request.method == 'POST' and request.FILES['file']:
        file = request.FILES['file']
        df = pd.read_excel(file, header=1)  # Usa header=1 para que tome la segunda fila como encabezado
        
        # Limpia los nombres de las columnas
        df.columns = df.columns.str.strip()  # Elimina espacios en blanco al inicio y al final de los nombres
        
        # Imprimir los nombres de las columnas
        print("Columnas en el DataFrame:", df.columns.tolist())  # Muestra los nombres de las columnas
        
        # Verificar que las columnas necesarias están presentes
        required_columns = [
            'Programa de Estudio', 'Mención', 'Plan', 'Semestre', 'Cód Asignatura',
            'Asignatura', 'Hrs Asignatura', 'Sección', 'Jornada', 'Cupo',
            'Cant. Alumnos', 'Modalidad', 'Subsección', 'Tipo Subsección',
            'Alumnos CFT', 'Alumnos IP', 'Alumnos UTC', 'Estado Sección',
            'Horas Plan. Sección + Subscción', 'Hrs Planificadas', 'Fecha Inicio', 'Fecha Término'
        ]
        
        # Comprobar si las columnas requeridas están en el DataFrame
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print("Columnas faltantes:", missing_columns)  # Imprimir las columnas que faltan
            return render(request, 'secciones/importar_secciones.html', {'error': f"Columnas faltantes: {', '.join(missing_columns)}"})
        
        df.fillna(0, inplace=True)

        # Definir las horas válidas para la importación
        horas_validas = [54, 72, 90, 108]
       
        # Iterar sobre el DataFrame y guardar los datos en la base de datos
        for _, row in df.iterrows():
            # Verificar si las horas de la asignatura están en las horas válidas
            if row['Hrs Asignatura'] in horas_validas:
                Seccion.objects.create(
                    programa_estudio=row['Programa de Estudio'],
                    mencion=row['Mención'],
                    plan=row['Plan'],
                    semestre=row['Semestre'],
                    cod_asignatura=row['Cód Asignatura'],
                    asignatura=row['Asignatura'],
                    hrs_asignatura=row['Hrs Asignatura'],
                    seccion=row['Sección'],
                    jornada=row['Jornada'],
                    cupo=row['Cupo'],
                    cant_alumnos=row['Cant. Alumnos'],
                    modalidad=row['Modalidad'],
                    subseccion=row['Subsección'],
                    tipo_subseccion=row['Tipo Subsección'],
                    alumnos_cft=row['Alumnos CFT'],
                    alumnos_ip=row['Alumnos IP'],
                    alumnos_utc=row['Alumnos UTC'],
                    estado_seccion=row['Estado Sección'],
                    horas_plan_seccion_subseccion=row['Horas Plan. Sección + Subscción'],
                    hrs_planificadas=row['Hrs Planificadas'],
                    fecha_inicio=row['Fecha Inicio'],
                    fecha_termino=row['Fecha Término'],
                )
        
        return redirect('listar_secciones')  # Redirige a la página de listado después de la importación

    return render(request, 'secciones/importar_secciones.html', {
        'current_section': 'secciones',
        'active_page': 'importar_secciones',
    })

def importar_salas(request):
    if request.method == 'POST' and request.FILES['file']:
        file = request.FILES['file']
        df = pd.read_excel(file, header=0)  # Usa header=0 si la segunda fila es el encabezado
        
        # Limpia los nombres de las columnas
        df.columns = df.columns.str.strip()  # Elimina espacios en blanco al inicio y al final de los nombres
        
        # Imprimir los nombres de las columnas
        print("Columnas en el DataFrame:", df.columns.tolist())  # Muestra los nombres de las columnas
        
        # Verificar que las columnas necesarias están presentes
        required_columns = [
            'Código ISO', 'Tipo Sala', 'Descripción', 'Sup. M2', 'Ubicación', 'Cupo Estándar'
        ]
        
        # Comprobar si las columnas requeridas están en el DataFrame
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print("Columnas faltantes:", missing_columns)  # Imprimir las columnas que faltan
            return render(request, 'salas/importar_salas.html', {'error': f"Columnas faltantes: {', '.join(missing_columns)}"})


        df.fillna(0, inplace=True)
        



        # Iterar sobre el DataFrame y guardar los datos en la base de datos
        for _, row in df.iterrows():
            Sala.objects.create(
                codigo_iso=row['Código ISO'],
                tipo_sala=row['Tipo Sala'],
                descripcion=row['Descripción'],
                sup_m2=row['Sup. M2'],
                ubicacion=row['Ubicación'],
                cupo_estandar=row['Cupo Estándar'],
            )
        
        return redirect('listar_salas')  # Redirige a la página de listado después de la importación

    return render(request, 'salas/importar_salas.html', {
        'current_section': 'salas',
        'active_page': 'importar_salas',
    })

def reset_seccion(request):
    # Ejecutar la función que reinicia la tabla
    reset_seccion_table()
    
    # Retornar una respuesta indicando que se ha realizado correctamente
    return redirect('listar_secciones') 

def reset_sala(request):
    # Ejecutar la función que reinicia la tabla
    reset_sala_table()
    
    # Retornar una respuesta indicando que se ha realizado correctamente
    return redirect('listar_salas') 

def asignar(request):
    # Ejecutar la función que reinicia la tabla
    asignar_bloques()
    
    # Retornar una respuesta indicando que se ha realizado correctamente
    
    return redirect('listar_secciones') 

def rellenar_disponibilidad(request):
    # Ejecutar la función que reinicia la tabla
    rellenar()
    
    # Retornar una respuesta indicando que se ha realizado correctamente
    return redirect('listar_salas') 
def prueba(request):
    # Ejecutar la función que reinicia la tabla
    asignar_horario_a_seccion(1)
    
    # Retornar una respuesta indicando que se ha realizado correctamente
    return HttpResponse("prueba completada.")