"""
URL configuration for horarios project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from horariosApp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    #INDEX
    path('', views.importar_secciones, name='inicio'),
    
    #SECCIONES
    path('importar_secciones/', views.importar_secciones, name='importar_secciones'),
    path('listar_secciones/', views.listar_secciones, name='listar_secciones'),
    path('crear_secciones', views.crear_secciones, name='crear_seccion'),
    path('secciones/editar/<int:id>/', views.editar_secciones, name='editar_secciones'),
    path('secciones/eliminar/<int:id>/', views.eliminar_secciones, name='eliminar_secciones'),
    path('reset-seccion/', views.reset_seccion, name='reset_seccion'),
    path('asignar/', views.asignar, name='asignar'),

    #SALAS
    path('importar_salas/', views.importar_salas, name='importar_salas'),
    path('listar_salas/', views.listar_salas, name='listar_salas'),
    path('crear_salas', views.crear_salas, name='crear_salas'),
    path('salas/editar/<int:id>/', views.editar_salas, name='editar_salas'),
    path('salas/eliminar/<int:id>/', views.eliminar_salas, name='eliminar_salas'),
    path('reset-sala/', views.reset_sala, name='reset_sala'),


    #HORARIO
    path('horario/', views.horarios_view, name='horarios'),

    #horariosala
    path('rellenar-disponibilidad/', views.rellenar_disponibilidad, name='rellenar_disponibilidad'),
    # pruba
    path('prueba/', views.prueba, name='prueba'),
]

