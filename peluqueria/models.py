# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.utils.encoding import smart_unicode
import datetime

# Create your models here.
class TipoTelefono(models.Model):
    nombre = models.CharField('Nombre', max_length=100)
    comentario = models.TextField('Comentario', null=True, blank=True)

    def __str__(self):
        return self.nombre

    def __unicode__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Tipo de telefono" 
        ordering = ('nombre',)
        
class Estado(models.Model):
    nombre = models.CharField('Nombre', max_length=100)
    comentario = models.TextField('Comentario', null=True, blank=True)

    def __str__(self):
        return self.nombre

    def __unicode__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Estados" 
        ordering = ('nombre',)



class MetodoPago(models.Model):
    nombre = models.CharField('Nombre', max_length=100)
    comentario = models.TextField('Comentario', null=True, blank=True)

    def __str__(self):
        return self.nombre

    def __unicode__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Metodos de Pago" 
        ordering = ('nombre',)

class TipoProducto(models.Model):
    nombre = models.CharField('Nombre', max_length=100)
    comentario = models.TextField('Comentario', null=True, blank=True)

    def __str__(self):
        return self.nombre

    def __unicode__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Tipos de Productos" 
        ordering = ('nombre',)

class Especialidad(models.Model):
    nombre = models.CharField('Nombre', max_length=100)
    comentario = models.TextField('Comentario', null=True, blank=True)

    def __str__(self):
        return self.nombre

    def __unicode__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Especialidades" 
        ordering = ('nombre',)

class Producto(models.Model):
    producto = models.CharField('Producto', max_length=100)
    tipo_producto = models.ForeignKey(TipoProducto)
    precio = models.FloatField('Precio', default=0)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.producto

    def dame_stock(self):
        stock = self.stock_set.all()
        actual = 0
        for st in stock:
            actual = actual + st.actual
        return actual

    def __unicode__(self):
        return self.producto


    class Meta:
        verbose_name_plural = "Productos" 
        ordering = ('producto',)

class Cliente(models.Model):
    nombre = models.CharField('Nombre', max_length=100)
    apellido = models.CharField('Apellido', max_length=100)
    mail = models.CharField('Mail', max_length=100, null=True, blank=True)
    nacimiento = models.DateField('Nacimiento', default=datetime.date.today)
    facebook = models.CharField('Facebook', max_length=100, null=True, blank=True)
    color_pelo = models.CharField('Color de pelo', max_length=100, null=True, blank=True)
    comentario = models.TextField('Comentario', null=True, blank=True)
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        return self.nombre
        
    def __unicode__(self):
        return self.nombre

    def dame_telefono(self):
        telefonos = self.telefono_set.all()
        for t in telefonos:
            if t.tipo_telefono.id == 1:
                return t.telefono
        return ''

    class Meta:
        verbose_name_plural = "Clientes" 
        ordering = ('nombre',)
        
class Empleado(models.Model):
    nombre = models.CharField('Nombre', max_length=100)
    apellido = models.CharField('Apellido', max_length=100)
    dni = models.CharField('Documento', max_length=30)
    mail = models.CharField('Mail', max_length=100, null=True, blank=True)
    direccion = models.CharField('Direccion', max_length=100, null=True, blank=True)
    experiencia = models.TextField('Experiencia', null=True, blank=True)
    especialidad = models.ForeignKey(Especialidad, null=True, blank=True)
    nacimiento = models.DateField('Nacimiento', default=datetime.date.today)
    comentario = models.TextField('Comentario', null=True, blank=True)
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        return self.nombre

    def __unicode__(self):
        return self.nombre

    def dame_telefono(self):
        telefonos = self.telefono_set.all()
        for t in telefonos:
            if t.tipo_telefono.id == 1:
                return t.telefono
        return ''

    def dame_facturacion_diaria(self):

        now = datetime.datetime.now()
        anio = str(now.year)
        
        if now.month < 10:
            mes = "0" + str(now.month)
        else:
            mes = str(now.month)
            
        if now.day < 10:
            dia = "0" + str(now.day)
        else:
            dia = str(now.day)   
        
        hoy = anio + mes + dia

        detalle = self.detallefactura_set.filter(factura__fecha_reporte=hoy,factura__activo=True)
        total = 0
        for d in detalle:
            total = total + d.total
        return total;

    def dame_facturacion_mensual(self):

        now = datetime.datetime.now()
        anio = str(now.year)
        
        if now.month < 10:
            mes = "0" + str(now.month)
        else:
            mes = str(now.month)
        
        hoy = anio + mes
        
        detalle = self.detallefactura_set.filter(factura__fecha_reporte__startswith=hoy,factura__activo=True)
        total = 0
        for d in detalle:
            total = total + d.total
        return total;


    class Meta:
        verbose_name_plural = "Empleados" 
        ordering = ('nombre',)

class Factura(models.Model):
    from datetime import datetime
    numero = models.CharField('Numero', max_length=100)
    fecha = models.DateTimeField('Fecha', default=datetime.now, blank=True)
    fecha_reporte = models.CharField('Fecha Reporte', max_length=20, null=True, blank=True)
    subtotal = models.FloatField('Precio', default=0)
    descuento = models.FloatField('Precio', default=0)
    total = models.FloatField('Precio', default=0)
    cliente = models.ForeignKey(Cliente)
    metodo_pago = models.ForeignKey(MetodoPago)
    estado = models.ForeignKey(Estado)
    comentario = models.TextField('Comentario', null=True, blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.numero

    def __unicode__(self):
        return self.numero

    class Meta:
        verbose_name_plural = "Facturas" 
        ordering = ('numero',)

class DetalleFactura(models.Model):
    factura = models.ForeignKey(Factura)
    producto = models.ForeignKey(Producto)
    cantidad = models.FloatField('Cantidad', default=0)
    empleado = models.ForeignKey(Empleado)
    descuento = models.FloatField('Descuento', default=0)
    precio = models.FloatField('Precio', default=0)
    total = models.FloatField('Total', default=0)

    def __str__(self):
        return self.factura.numero

    def __unicode__(self):
        return self.factura.numero

    class Meta:
        verbose_name_plural = "Detalle Facturas" 
        ordering = ('factura',)

class Stock(models.Model):
    producto = models.ForeignKey(Producto)
    fecha = models.DateField('Fecha', default=datetime.date.today)
    inicial = models.FloatField('Inicial', default=0)
    actual = models.FloatField('Actual', default=0)
    comentario = models.TextField('Comentario', null=True, blank=True)
    costo = models.FloatField('Costo', default=0)
    
    def __str__(self):
        return self.producto.producto

    def __unicode__(self):
        return self.producto.producto

    class Meta:
        verbose_name_plural = "Stock" 
        ordering = ('producto',)
        
class Telefono(models.Model):
    telefono = models.CharField('Telefono', max_length=100)
    tipo_telefono = models.ForeignKey(TipoTelefono)
    comentario = models.TextField('Comentario', null=True, blank=True)
    empleado = models.ForeignKey(Empleado, null=True, blank=True)
    cliente = models.ForeignKey(Cliente, null=True, blank=True)
    
    def __str__(self):
        return self.telefono

    def __unicode__(self):
        return self.telefono

    class Meta:
        verbose_name_plural = "Telefonos" 
        ordering = ('telefono',)
        
class HorariosEmpleados(models.Model):
    TURNOS_EMPLEADOS = (
        ('MA', 'Manana'),
        ('TA', 'Tarde'),
        ('NO', 'Noche'),
        ('FA', 'Franco'),
    )
    empleado = models.ForeignKey(Empleado)
    fecha = models.CharField('Fecha', max_length=8)
    turno = models.CharField(max_length=2, choices=TURNOS_EMPLEADOS, default='MA')
    comentario = models.TextField('Comentario', null=True, blank=True)
    
    def __str__(self):
        return self.empleado.nombre

    def __unicode__(self):
        return self.empleado.nombre

    class Meta:
        verbose_name_plural = "Horarios Empleados" 
        ordering = ('fecha',)