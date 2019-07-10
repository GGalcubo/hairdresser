"""myproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.conf.urls import include, url
from django.contrib import admin

from django.conf import settings
from django.conf.urls.static import static

from peluqueria import views

urlpatterns = [
    #Admin
    url(r'^admin/', admin.site.urls),
    
    #Sistema
    url(r'^ingresar/', views.ingresar, name='ingresar'),
    url(r'^recuperar/', views.recuperar, name='recuperar'),
    url(r'^dashboard/', views.dashboard, name='dashboard'),
    url(r'^salir/', views.salir, name='salir'),

    #Facturas
    url(r'^facturas/', views.facturas, name='facturas'),
    url(r'^guardar_factura/', views.guardar_factura, name='guardar_factura'),
    url(r'^guardar_factura_producto/', views.guardar_factura_producto, name='guardar_factura_producto'),
    url(r'^dame_factura/', views.dame_factura, name='dame_factura'),
    url(r'^eliminar_factura/', views.eliminar_factura, name='eliminar_factura'),

    #Clientes
    url(r'^clientes/', views.clientes, name='clientes'),
    url(r'^guardar_cliente/', views.guardar_cliente, name='guardar_cliente'),
    url(r'^dame_cliente/', views.dame_cliente, name='dame_cliente'),
    url(r'^eliminar_cliente/', views.eliminar_cliente, name='eliminar_cliente'),

    url(r'^imprimir_ticket/', views.imprimir_ticket, name='imprimir_ticket'),

    #Empleados
    url(r'^empleados/', views.empleados, name='empleados'),
    url(r'^guardar_empleado/', views.guardar_empleado, name='guardar_empleado'),
    url(r'^dame_empleado/', views.dame_empleado, name='dame_empleado'),
    url(r'^eliminar_empleado/', views.eliminar_empleado, name='eliminar_empleado'),
    
    #Productos
    url(r'^productos/', views.productos, name='productos'),
    url(r'^guardar_producto/', views.guardar_producto, name='guardar_producto'),
    url(r'^dame_producto/', views.dame_producto, name='dame_producto'),
    url(r'^eliminar_producto/', views.eliminar_producto, name='eliminar_producto'),
    url(r'^dame_precio_producto/', views.dame_precio_producto, name='dame_precio_producto'),
    

    #Horario
    url(r'^reporte_horarios/', views.reporte_horarios, name='reporte_horarios'),
    url(r'^guardar_horario/', views.guardar_horario, name='guardar_horario'),
    url(r'^dame_empleado_horario/', views.dame_empleado_horario, name='dame_empleado_horario'),
    url(r'^repetir_semana_anterior/', views.repetir_semana_anterior, name='repetir_semana_anterior'),
    
    #Reportes
    url(r'^reporte_facturacion/', views.reporte_facturacion, name='reporte_facturacion'),
    
    url(r'^$', views.index, name='index'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)