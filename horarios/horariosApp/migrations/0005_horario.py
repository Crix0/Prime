# Generated by Django 5.1.1 on 2024-11-14 04:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('horariosApp', '0004_seccion_cant_bloques'),
    ]

    operations = [
        migrations.CreateModel(
            name='Horario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('disponibilidad_sala', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='horariosApp.disponibilidadsala')),
                ('seccion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='horariosApp.seccion')),
            ],
            options={
                'unique_together': {('seccion', 'disponibilidad_sala')},
            },
        ),
    ]
