# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-26 14:39
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('peluqueria', '0002_auto_20160925_2117'),
    ]

    operations = [
        migrations.CreateModel(
            name='HorariosEmpleados',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_inicio', models.DateField(default=datetime.date.today, verbose_name='Fecha Inicio')),
                ('fecha_fin', models.DateField(default=datetime.date.today, verbose_name='Fecha Fin')),
                ('turno', models.CharField(choices=[('MA', 'Manana'), ('TA', 'Tarde'), ('NO', 'Noche')], default='MA', max_length=2)),
                ('comentario', models.TextField(blank=True, null=True, verbose_name='Comentario')),
                ('empleado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='peluqueria.Empleado')),
            ],
            options={
                'ordering': ('fecha_inicio',),
                'verbose_name_plural': 'Horarios Empleados',
            },
        ),
        migrations.CreateModel(
            name='Telefono',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('telefono', models.CharField(max_length=100, verbose_name='Telefono')),
                ('comentario', models.TextField(blank=True, null=True, verbose_name='Comentario')),
                ('cliente', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='peluqueria.Cliente')),
                ('empleado', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='peluqueria.Empleado')),
            ],
            options={
                'ordering': ('telefono',),
                'verbose_name_plural': 'Telefonos',
            },
        ),
        migrations.CreateModel(
            name='TipoTelefono',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, verbose_name='Nombre')),
                ('comentario', models.TextField(blank=True, null=True, verbose_name='Comentario')),
            ],
            options={
                'ordering': ('nombre',),
                'verbose_name_plural': 'Tipo de telefono',
            },
        ),
        migrations.AddField(
            model_name='stock',
            name='costo',
            field=models.FloatField(default=0, verbose_name='Costo'),
        ),
        migrations.AlterField(
            model_name='stock',
            name='fecha',
            field=models.DateField(default=datetime.date.today, verbose_name='Fecha'),
        ),
        migrations.AddField(
            model_name='telefono',
            name='tipo_telefono',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='peluqueria.TipoTelefono'),
        ),
    ]
