from django.contrib import admin
from .models import Especialidad, Cliente, Empleado, MetodoPago, TipoProducto, Producto, Factura, DetalleFactura, Stock, Estado, TipoTelefono, Telefono, HorariosEmpleados
# Register your models here.
class HorariosEmpleadosInline(admin.TabularInline):
    model = HorariosEmpleados
    extra = 0
    
class TelefonoInline(admin.TabularInline):
    model = Telefono
    extra = 0

class StockInline(admin.TabularInline):
    model = Stock
    extra = 0

class DetalleFacturaInline(admin.TabularInline):
    model = DetalleFactura
    extra = 0

class StockAdmin(admin.ModelAdmin):
    list_max_show_all = 1000
    list_per_page = 400

    list_display = ('producto', 'fecha', 'inicial', 'actual', 'comentario')
    fieldsets = (
        ('Principal', {
            'classes': ('wide', 'extrapretty'),
            'fields': ('producto', 'fecha', 'inicial', 'actual', 'comentario')
        }),
    ) 

class FacturaAdmin(admin.ModelAdmin):
    inlines = [
        DetalleFacturaInline
    ]
    list_max_show_all = 1000
    list_per_page = 400

    list_display = ('numero', 'fecha','fecha_reporte', 'total', 'cliente', 'metodo_pago', 'estado', 'comentario','activo')
    fieldsets = (
        ('Principal', {
            'classes': ('wide', 'extrapretty'),
            'fields': ('numero', 'fecha','fecha_reporte', 'total', 'cliente', 'metodo_pago', 'estado', 'comentario','activo')
        }),
    )

class ProductoAdmin(admin.ModelAdmin):
    inlines = [
        StockInline
    ]
    list_max_show_all = 1000
    list_per_page = 400

    list_display = ('producto', 'tipo_producto', 'precio','activo')
    fieldsets = (
        ('Principal', {
            'classes': ('wide', 'extrapretty'),
            'fields': ('producto', 'tipo_producto', 'precio','activo')
        }),
    )

class ClienteAdmin(admin.ModelAdmin):
    inlines = [TelefonoInline]
    list_max_show_all = 1000
    list_per_page = 400

    list_display = ('nombre', 'apellido', 'mail', 'nacimiento', 'facebook', 'color_pelo', 'comentario','activo')
    fieldsets = (
        ('Principal', {
            'classes': ('wide', 'extrapretty'),
            'fields': ('nombre', 'apellido', 'mail', 'nacimiento', 'facebook', 'color_pelo', 'comentario','activo')
        }),
    )
    
class EmpleadoAdmin(admin.ModelAdmin):
    inlines = [TelefonoInline, HorariosEmpleadosInline]
    list_max_show_all = 1000
    list_per_page = 400

    list_display = ('nombre', 'apellido', 'dni', 'mail', 'experiencia', 'especialidad', 'nacimiento', 'comentario','activo')
    fieldsets = (
        ('Principal', {
            'classes': ('wide', 'extrapretty'),
            'fields': ('nombre', 'apellido', 'dni', 'mail', 'experiencia', 'especialidad', 'nacimiento', 'comentario','activo')
        }),
    )

class HorariosEmpleadosAdmin(admin.ModelAdmin):
    list_max_show_all = 1000
    list_per_page = 400
    list_display = ('empleado', 'fecha', 'turno')
    fieldsets = (
        ('Principal', {
            'classes': ('wide', 'extrapretty'),
            'fields': ('empleado', 'fecha', 'turno', 'comentario')
        }),
    )



admin.site.register(Estado)
admin.site.register(MetodoPago)
admin.site.register(TipoProducto)
admin.site.register(Especialidad)
admin.site.register(DetalleFactura)
admin.site.register(TipoTelefono)
admin.site.register(Telefono)
admin.site.register(HorariosEmpleados, HorariosEmpleadosAdmin)
admin.site.register(Producto, ProductoAdmin)
admin.site.register(Cliente, ClienteAdmin)
admin.site.register(Empleado, EmpleadoAdmin) 
admin.site.register(Factura, FacturaAdmin) 
admin.site.register(Stock, StockAdmin)