#-*- coding: utf-8 -*-
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.template import loader
from django.http import HttpResponse
from django.utils.translation import ugettext
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from .models import Empleado, Cliente, Factura, TipoTelefono, Telefono, Especialidad, MetodoPago, Estado, Producto, DetalleFactura, TipoProducto, Stock, HorariosEmpleados
import json
import datetime


# Create your views here.
def index(request):
    mensaje = 'INDEX'
    
    context = {'mensaje': mensaje,}
    return render(request, 'index.html', context)

def recuperar(request):

    dict = {'error': '', 'result': ''}

    email = request.POST.get('email')

    try:
        usuario = User.objects.get(username=email) 
        error = ''
        result = 'Se le envió el nuevo password (no olvides revisar el spam).'
    except ObjectDoesNotExist:
        error = 'Usuario inexistente!'
        result = ''
    
    dict = {'error': error, 'result': result}

    return HttpResponse(json.dumps(dict), content_type="application/json")

# Create your views here.
def ingresar(request):
    mensaje = ''

    if request.method == 'GET':
        pass
    elif request.method == 'POST':

        username = request.POST.get('email')
        password = request.POST.get('password')

        if username == '' or password == '':
            mensaje = 'Ambos campos son obligatorios.'
        else:
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect(reverse('clientes'))
                else:
                    mensaje = 'La cuenta está inactiva. Comuníquese con el administrador.'
            else:        
                mensaje = 'Nombre de usuario o contraseña no válido.'


    context = {'mensaje': mensaje,}
    return render(request, 'ingresar.html', context)

def salir(request):
    logout(request)
    return redirect(reverse('ingresar'))

@login_required    
def dashboard(request):
    mensaje = ''
    context = {'mensaje': mensaje,}
    return render(request, 'dashboard.html', context)

@login_required    
def facturas(request):
    mensaje = ''
    facturas = Factura.objects.all()
    empleados = Empleado.objects.filter(activo=True)
    clientes = Cliente.objects.filter(activo=True)
    metodos_pago = MetodoPago.objects.all()
    estados = Estado.objects.all()
    productos = Producto.objects.filter(activo=True)
    estado_inicial = 'Inicial'
    id_estado_inicial = 1
    id_factura = ''
    try:
        factura_uno = Factura.objects.order_by('-numero')[0].numero
        pedido = factura_uno.split('-')[1]
        nuevoNumero = str(int(pedido)+1)
        cerosCantidad = 8 - len(nuevoNumero)
        ceros = '0' * cerosCantidad
        numero_factura = factura_uno.split('-')[0] + '-' + ceros + nuevoNumero
    except:
        numero_factura = '0001-00000001'

    context = {'mensaje': mensaje, 'facturas': facturas, 'metodos_pago': metodos_pago, 'estados': estados, 'empleados': empleados, 'productos': productos, 'clientes': clientes, 'estado_inicial': estado_inicial, 'id_estado_inicial': id_estado_inicial, 'numero_factura': numero_factura, 'id_factura': id_factura }
    return render(request, 'facturas.html', context)
 
@login_required    
def dame_factura(request):
    id_factura = request.GET.get('id_factura')
    factura = Factura.objects.get(id=id_factura)

    if factura.metodo_pago:
        metodo_pago = factura.metodo_pago.id
    else:
        metodo_pago = 0

    detalle = []
    dict_detalle = {}
    i = 0
    for df in factura.detallefactura_set.all():
        dict_detalle = {}
        dict_detalle['prod'] = df.producto.producto
        dict_detalle['empl'] = df.empleado.nombre + ' ' + df.empleado.apellido
        dict_detalle['cant'] = df.cantidad
        dict_detalle['precio'] = df.precio
        dict_detalle['tota'] = df.total
        detalle.insert(i, dict_detalle)
        i = i + 1


    fecha = factura.fecha.strftime('%d-%m-%Y')
    dict = {'id_factura': factura.id, 'numero': factura.numero, 'cliente': factura.cliente.nombre +' '+ factura.cliente.apellido, 'fecha': fecha, 'total': factura.total, 'descuento': factura.descuento, 'subtotal': factura.subtotal,'comentario': factura.comentario, 'metodo_pago': metodo_pago, 'estado': factura.estado.nombre, 'detalle': detalle }
    return HttpResponse(json.dumps(dict), content_type="application/json")

@login_required    
def eliminar_factura(request):
    id_factura = request.POST.get('id_factura')
    factura = Factura.objects.get(id=id_factura)
    factura.estado = Estado.objects.get(id=3)
    factura.activo = False
    factura.save()

    for detalle in factura.detallefactura_set.all():
        restante = detalle.cantidad
        for stock in detalle.producto.stock_set.all().order_by('-fecha'):
            if stock.inicial != stock.actual and restante > 0:
                if restante > (stock.inicial - stock.actual):
                    stock.actual = stock.inicial
                    restante = restante - (stock.inicial - stock.actual)
                else:
                    stock.actual = stock.actual + restante
                    restante = 0
                stock.save()


    dict = {'id_factura': factura.id }
    return HttpResponse(json.dumps(dict), content_type="application/json")

@login_required    
def guardar_factura(request):
    mensaje = ''
    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        try:
            id_cliente_seleccionado = request.POST.get('id_cliente_seleccionado')
            id_factura  = request.POST.get('id_factura')
            fecha       = request.POST.get('fecha')
            subtotal    = request.POST.get('subtotal')
            descuento   = request.POST.get('descuento')
            total       = request.POST.get('total')
            comentario  = request.POST.get('comentario')
            numero_factura  = request.POST.get('numero_factura')
            id_estado_inicial  = request.POST.get('id_estado_inicial')
            id_metodo_pago     = request.POST.get('id_metodo_pago')

            cliente = Cliente.objects.get(id=id_cliente_seleccionado)
            metodo_pago = MetodoPago.objects.get(id=id_metodo_pago)
            estado = Estado.objects.get(id=2)
            fecha_fact = fecha[6:] +'-'+ fecha[3:5] +'-'+ fecha[0:2]
            fecha_reportes = fecha[6:] + fecha[3:5] + fecha[0:2]

            if id_factura == "":
                factura = Factura()
            else:
                factura = Factura.objects.get(id=id_factura)

            factura.numero              = numero_factura
            factura.cliente             = cliente
            factura.fecha               = fecha_fact
            factura.fecha_reporte       = fecha_reportes
            factura.subtotal            = float(subtotal)
            factura.descuento           = float(descuento)
            factura.total               = float(total)
            factura.estado              = estado
            factura.metodo_pago         = metodo_pago
            factura.comentario          = comentario
            factura.save()

            id_factura = factura.id

        except Exception as e:
            mensaje = str(e)
            
    dict = {'error': mensaje, 'id_factura': id_factura }
    return HttpResponse(json.dumps(dict), content_type="application/json")


@login_required    
def guardar_factura_producto(request):

    mensaje = ''
    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        try:
            id_factura  = request.POST.get('id_factura')
            id_prod  = request.POST.get('id_prod')
            id_empl  = request.POST.get('id_empl')
            cant  = request.POST.get('cant')
            precio  = request.POST.get('precio')
            total  = request.POST.get('total')

            factura = Factura.objects.get(id=id_factura)
            producto = Producto.objects.get(id=id_prod)
            empleado = Empleado.objects.get(id=id_empl)

            df = DetalleFactura()
            df.factura  = factura
            df.producto = producto
            df.cantidad = float(cant)
            df.precio = float(precio)
            df.empleado = empleado
            df.total    = float(total)
            df.save()

            stocks = producto.stock_set.all().order_by('fecha')
            restante = float(cant)
            for s in stocks:
                if s.actual > 0 and restante > 0:
                    if s.actual > restante:
                        s.actual = s.actual - restante
                        restante = 0
                    else:
                        restante = restante - s.actual
                        s.actual = 0
                    s.save()



        except Exception as e:
            mensaje = str(e)

    dict = {'error': mensaje, }
    return HttpResponse(json.dumps(dict), content_type="application/json")

@login_required
def empleados(request):
    mensaje = ''
    empleados = Empleado.objects.filter(activo=True)
    especialidades = Especialidad.objects.all()
    context = {'mensaje': mensaje, 'empleados': empleados, 'especialidades': especialidades, }
    return render(request, 'empleados.html', context)

@login_required    
def dame_empleado(request):
    id_empleado = request.GET.get('id_empleado')
    empleado = Empleado.objects.get(id=id_empleado)
    if empleado.especialidad:
        id_espe = empleado.especialidad.id
    else:
        id_espe = 0
    nac = empleado.nacimiento.strftime('%d-%m-%Y')
    dict = {'id_empleado': empleado.id, 'nombre': empleado.nombre, 'apellido': empleado.apellido, 'nacimiento': nac, 'telefono': empleado.dame_telefono(), 'email': empleado.mail, 'direccion': empleado.direccion,'comentario': empleado.comentario, 'experiencia': empleado.experiencia, 'documento': empleado.dni, 'id_especialidad':id_espe }
    return HttpResponse(json.dumps(dict), content_type="application/json")

@login_required    
def eliminar_empleado(request):
    id_empleado = request.POST.get('id_empleado')
    empleado = Empleado.objects.get(id=id_empleado)
    empleado.activo = False
    empleado.save()

    dict = {'id_empleado': empleado.id }
    return HttpResponse(json.dumps(dict), content_type="application/json")

@login_required    
def guardar_empleado(request):
    mensaje = ''
    
    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        try:
            id_empleado = request.POST.get('id_empleado')
            nombre      = request.POST.get('nombre')
            apellido    = request.POST.get('apellido')
            telefono    = request.POST.get('telefono')
            email       = request.POST.get('email')
            direccion   = request.POST.get('direccion')
            nacimiento  = request.POST.get('nacimiento')
            comentario  = request.POST.get('comentario')
            experiencia = request.POST.get('experiencia')
            documento   = request.POST.get('documento')
            id_especialidad = request.POST.get('especialidad')

            if id_empleado == "":
                empleado = Empleado()
            else:
                empleado = Empleado.objects.get(id=id_empleado)
                
            empleado.nombre = nombre
            empleado.apellido = apellido
            empleado.mail = email
            empleado.direccion = direccion

            if nacimiento == '':
                nacimiento = '1900-01-01'
            else:
                nacimiento = nacimiento[6:] +'-'+ nacimiento[3:5] +'-'+ nacimiento[0:2]
                
            empleado.nacimiento = nacimiento
            empleado.comentario = comentario
            empleado.experiencia = experiencia
            empleado.dni = documento
            empleado.especialidad = Especialidad.objects.get(id=id_especialidad)
            empleado.save()
            
            if telefono != '':
                if id_empleado == "":
                    tel = Telefono()
                    tel.tipo_telefono = TipoTelefono.objects.get(id=1)
                    tel.telefono = telefono
                    tel.empleado = empleado
                    tel.save()
                else:
                    if len(empleado.telefono_set.all()) > 0:
                        for t in empleado.telefono_set.all():
                            if t.tipo_telefono.id == 1:
                                t.telefono = telefono
                                t.save()
                    else:
                        tel = Telefono()
                        tel.tipo_telefono = TipoTelefono.objects.get(id=1)
                        tel.telefono = telefono
                        tel.empleado = empleado
                        tel.save()

        except Exception as e:
            mensaje = str(e)
            
    dict = {'error': mensaje}
    return HttpResponse(json.dumps(dict), content_type="application/json")
    
@login_required    
def clientes(request):
    mensaje = ''
    id_cliente = ''
    clientes = Cliente.objects.filter(activo=True)
    context = {'mensaje': mensaje, 'clientes': clientes, 'id_cliente': id_cliente}
    return render(request, 'clientes.html', context)

@login_required    
def dame_cliente(request):
    id_cliente = request.GET.get('id_cliente')
    cliente = Cliente.objects.get(id=id_cliente)
    nac = cliente.nacimiento.strftime('%d-%m-%Y')
    dict = {'id_cliente': cliente.id, 'nombre': cliente.nombre, 'apellido': cliente.apellido, 'nacimiento': nac, 'color_pelo': cliente.color_pelo, 'telefono': cliente.dame_telefono(), 'email': cliente.mail, 'comentario': cliente.comentario,}
    return HttpResponse(json.dumps(dict), content_type="application/json")
    
@login_required    
def eliminar_cliente(request):
    id_cliente = request.POST.get('id_cliente')
    cliente = Cliente.objects.get(id=id_cliente)
    cliente.activo = False
    cliente.save()

    dict = {'id_cliente': cliente.id }
    return HttpResponse(json.dumps(dict), content_type="application/json")

@login_required    
def guardar_cliente(request):
    mensaje = ''
    
    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        try:
            id_cliente  = request.POST.get('id_cliente')
            nombre      = request.POST.get('nombre')
            apellido    = request.POST.get('apellido')
            telefono    = request.POST.get('telefono')
            email       = request.POST.get('email')
            nacimiento  = request.POST.get('nacimiento')
            color_pelo  = request.POST.get('color_pelo')
            comentario  = request.POST.get('comentario')

            if id_cliente == "":
                cliente = Cliente()
            else:
                cliente = Cliente.objects.get(id=id_cliente)
                
            cliente.nombre = nombre
            cliente.apellido = apellido
            cliente.mail = email
            
            if nacimiento == '':
                nacimiento = '1900-01-01'
            else:
                nacimiento = nacimiento[6:] +'-'+ nacimiento[3:5] +'-'+ nacimiento[0:2]
                
            cliente.nacimiento = nacimiento
            cliente.color_pelo = color_pelo
            cliente.comentario = comentario
            cliente.save()
            
            if telefono != '':
                if id_cliente == "":
                    tel = Telefono()
                    tel.tipo_telefono = TipoTelefono.objects.get(id=1)
                    tel.telefono = telefono
                    tel.cliente = cliente
                    tel.save()
                else:
                    if len(cliente.telefono_set.all()) > 0:
                        for t in cliente.telefono_set.all():
                            if t.tipo_telefono.id == 1:
                                t.telefono = telefono
                                t.save()
                    else:
                        tel = Telefono()
                        tel.tipo_telefono = TipoTelefono.objects.get(id=1)
                        tel.telefono = telefono
                        tel.cliente = cliente
                        tel.save()

        except Exception as e:
            mensaje = str(e)
            
    dict = {'error': mensaje}
    return HttpResponse(json.dumps(dict), content_type="application/json")

@login_required    
def productos(request):
    mensaje = ''
    id_producto = ''
    productos = Producto.objects.filter(activo=True)
    tipos_producto = TipoProducto.objects.all()
    context = {'mensaje': mensaje, 'productos': productos, 'id_producto': id_producto, 'tipos_producto': tipos_producto}
    return render(request, 'productos.html', context)

@login_required    
def guardar_producto(request):
    mensaje = ''

    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        try:
            id_producto         = request.POST.get('id_producto')
            nombre              = request.POST.get('nombre')
            precio              = request.POST.get('precio')
            tipo_prod           = request.POST.get('tipo_prod')
            cant_stock          = request.POST.get('cant_stock')
            costo_stock         = request.POST.get('costo_stock')
            comentario_stock    = request.POST.get('comentario_stock')

            if id_producto == "":
                producto = Producto()
            else:
                producto = Producto.objects.get(id=id_producto)
                
            producto.producto = nombre
            producto.precio = precio
            producto.tipo_producto = TipoProducto.objects.get(id=tipo_prod)
            producto.save()

            if cant_stock != "" and cant_stock != 0:
                stock = Stock()
                stock.inicial = cant_stock
                stock.actual = cant_stock
                stock.costo = costo_stock
                stock.comentario = comentario_stock
                stock.producto = producto
                stock.save()

        except Exception as e:
            mensaje = str(e)

    dict = {'error': mensaje}
    return HttpResponse(json.dumps(dict), content_type="application/json")

@login_required    
def dame_producto(request):
    id_producto = request.GET.get('id_producto')
    producto = Producto.objects.get(id=id_producto)

    detalle = []
    dict_detalle = {}
    i = 0
    for st in producto.stock_set.all():
        if st.actual > 0:
            dict_detalle = {}
            dict_detalle['fecha'] = st.fecha.strftime('%d-%m-%Y')
            dict_detalle['inicial'] = st.inicial
            dict_detalle['actual'] = st.actual
            dict_detalle['costo'] = st.costo
            dict_detalle['comentario'] = st.comentario
            detalle.insert(i, dict_detalle)
            i = i + 1

    dict = {'id_producto': producto.id, 'nombre': producto.producto, 'tipo_prod': producto.tipo_producto.id, 'precio': producto.precio, 'actual': producto.dame_stock(), 'detalle':detalle }
    return HttpResponse(json.dumps(dict), content_type="application/json")

@login_required    
def eliminar_producto(request):
    id_producto = request.POST.get('id_producto')
    producto = Producto.objects.get(id=id_producto)
    producto.activo = False
    producto.save()

    dict = {'id_producto': producto.id }
    return HttpResponse(json.dumps(dict), content_type="application/json")

@login_required    
def dame_precio_producto(request):
    id_producto = request.POST.get('id_producto')
    producto = Producto.objects.get(id=id_producto)
    valor = producto.precio

    dict = {'valor': valor }
    return HttpResponse(json.dumps(dict), content_type="application/json")

@login_required    
def reporte_horarios(request):
    from datetime import datetime,timedelta

    mensaje = ''
    id_empleado = ''
    empleados = Empleado.objects.filter(activo=True)

    if request.method == 'GET':
        fecha_int = ''
        semana = ''
    elif request.method == 'POST':
        fecha_int = request.POST.get('fecha_int')
        semana = request.POST.get('semana')

    fecha_desde, fecha_hasta, fecha_int = dame_fechas_reportes(fecha_int, semana)

    empl_list = []
    empl_dict = {}

    TURNOS_EMPLEADOS = (
        ('MA', '8 a 16'),
        ('IN', '11 a 19'),
        ('TA', '12 a 20'),
        ('FE', '9 a 15'),
        ('FA', 'Franco'),
    )

    turnos_dict = {}
    turnos_dict['MA'] = '8 a 16'
    turnos_dict['IN'] = '11 a 19'
    turnos_dict['TA'] = '12 a 20'
    turnos_dict['FE'] = '9 a 15'
    turnos_dict['FA'] = 'Franco'

    for empleado in empleados:

        empl_dict = {}

        empl_dict["id"] = empleado.id
        empl_dict["nombre"] = empleado.nombre + ' ' + empleado.apellido


        fecha_inicio = fecha_desde.split("/")

        if len(fecha_inicio[0]) == 1:
            dia = "0" + fecha_inicio[0]
        else:
            dia = fecha_inicio[0]
        mes = fecha_inicio[1]

        if len(mes) == 1:
            mes = "0" + str(mes)
        else:
            mes = str(mes)

        ano = fecha_inicio[2]

        count = 0
        while (count < 7):
            fecha = str(ano) + str(mes) + str(dia)
            horario = empleado.horariosempleados_set.filter(fecha=fecha)

            if len(horario) > 0:
                turno = horario[0].turno
            else:
                turno = 'MA'

            if count == 0:
                lunes = turno
                if turno == 'MA':
                    empl_dict["lunes_alert"] = 'success'
                elif turno == 'IN':
                    empl_dict["lunes_alert"] = 'info'
                elif turno == 'TA':
                    empl_dict["lunes_alert"] = 'warning'
                elif turno == 'FE':
                    empl_dict["lunes_alert"] = 'feriado'
                elif turno == 'FA':
                    empl_dict["lunes_alert"] = 'danger'
                empl_dict["lunes"] = turnos_dict.get(lunes)
            elif count == 1:
                martes = turno
                if turno == 'MA':
                    empl_dict["martes_alert"] = 'success'
                elif turno == 'IN':
                    empl_dict["martes_alert"] = 'info'
                elif turno == 'TA':
                    empl_dict["martes_alert"] = 'warning'
                elif turno == 'FE':
                    empl_dict["martes_alert"] = 'feriado'
                elif turno == 'FA':
                    empl_dict["martes_alert"] = 'danger'
                empl_dict["martes"] = turnos_dict.get(martes)
            elif count == 2:
                miercoles = turno
                if turno == 'MA':
                    empl_dict["miercoles_alert"] = 'success'
                elif turno == 'IN':
                    empl_dict["miercoles_alert"] = 'info'
                elif turno == 'TA':
                    empl_dict["miercoles_alert"] = 'warning'
                elif turno == 'FE':
                    empl_dict["miercoles_alert"] = 'feriado'
                elif turno == 'FA':
                    empl_dict["miercoles_alert"] = 'danger'
                empl_dict["miercoles"] = turnos_dict.get(miercoles)
            elif count == 3:
                jueves = turno
                if turno == 'MA':
                    empl_dict["jueves_alert"] = 'success'
                elif turno == 'IN':
                    empl_dict["jueves_alert"] = 'info'
                elif turno == 'TA':
                    empl_dict["jueves_alert"] = 'warning'
                elif turno == 'FE':
                    empl_dict["jueves_alert"] = 'feriado'
                elif turno == 'FA':
                    empl_dict["jueves_alert"] = 'danger'
                empl_dict["jueves"] = turnos_dict.get(jueves)
            elif count == 4:
                viernes = turno
                if turno == 'MA':
                    empl_dict["viernes_alert"] = 'success'
                elif turno == 'IN':
                    empl_dict["viernes_alert"] = 'info'
                elif turno == 'TA':
                    empl_dict["viernes_alert"] = 'warning'
                elif turno == 'FE':
                    empl_dict["viernes_alert"] = 'feriado'
                elif turno == 'FA':
                    empl_dict["viernes_alert"] = 'danger'
                empl_dict["viernes"] = turnos_dict.get(viernes)
            elif count == 5:
                sabado = turno
                if turno == 'MA':
                    empl_dict["sabado_alert"] = 'success'
                elif turno == 'IN':
                    empl_dict["sabado_alert"] = 'info'
                elif turno == 'TA':
                    empl_dict["sabado_alert"] = 'warning'
                elif turno == 'FE':
                    empl_dict["sabado_alert"] = 'feriado'
                elif turno == 'FA':
                    empl_dict["sabado_alert"] = 'danger'
                empl_dict["sabado"] = turnos_dict.get(sabado)
            elif count == 6:
                domingo = turno
                if turno == 'MA':
                    empl_dict["domingo_alert"] = 'success'
                elif turno == 'IN':
                    empl_dict["domingo_alert"] = 'info'
                elif turno == 'TA':
                    empl_dict["domingo_alert"] = 'warning'
                elif turno == 'FE':
                    empl_dict["domingo_alert"] = 'feriado'
                elif turno == 'FA':
                    empl_dict["domingo_alert"] = 'danger'
                empl_dict["domingo"] = turnos_dict.get(domingo)

            fecha_py = datetime.strptime(fecha, '%Y%m%d')

            dias = timedelta(days=1)
            fecha_py = fecha_py+dias
            ano = fecha_py.year
            mes = fecha_py.month
            dia = fecha_py.day

            if dia < 10:
                dia = "0" + str(dia)
            else:
                dia = str(dia)

            if mes < 10:
                mes = "0" + str(mes)
            else:
                mes = str(mes)

            count = count + 1

        empl_list.append(empl_dict)

    #####################################################
    ####### ESTO ES LO DE LA FECHA QUE HICIMOS HOY ######

    from datetime import datetime
    fecha_py = datetime.strptime(fecha_int, '%Y%m%d')
    dias = timedelta(days=1)

    fecha_lunes = str(fecha_py.day) + '/' + str(fecha_py.month)

    fecha_py = fecha_py + dias
    fecha_martes = str(fecha_py.day) + '/' + str(fecha_py.month)

    fecha_py = fecha_py + dias
    fecha_miercoles = str(fecha_py.day) + '/' + str(fecha_py.month)

    fecha_py = fecha_py + dias
    fecha_jueves = str(fecha_py.day) + '/' + str(fecha_py.month)

    fecha_py = fecha_py + dias
    fecha_viernes = str(fecha_py.day) + '/' + str(fecha_py.month)

    fecha_py = fecha_py + dias
    fecha_sabado = str(fecha_py.day) + '/' + str(fecha_py.month)

    fecha_py = fecha_py + dias
    fecha_domingo = str(fecha_py.day) + '/' + str(fecha_py.month)

    ######################################################

    context = {'mensaje': mensaje, 'empl_list':empl_list, 'empleados': empleados, 'id_empleado': id_empleado, 'turnos': TURNOS_EMPLEADOS, 'fecha_desde':fecha_desde, 'fecha_hasta':fecha_hasta, 'fecha_int': fecha_int, 'fecha_lunes': fecha_lunes, 'fecha_martes': fecha_martes, 'fecha_miercoles': fecha_miercoles, 'fecha_jueves': fecha_jueves, 'fecha_viernes': fecha_viernes, 'fecha_sabado': fecha_sabado, 'fecha_domingo': fecha_domingo }
    return render(request, 'reporte_horarios.html', context)

@login_required    
def dame_empleado_horario(request):
    id_empleado = request.POST.get('id_empleado')
    fecha  = request.POST.get('fecha_inicio')
    empleado = Empleado.objects.get(id=int(id_empleado))
    nombre = empleado.nombre + ' ' + empleado.apellido

    count = 0
    while (count < 7):
        horario = empleado.horariosempleados_set.filter(fecha=fecha)
        comentario = ''
        if len(horario) > 0:
            comentario = horario[0].comentario
            turno = horario[0].turno
        else:
            turno = 'MA'

        if count == 0:
            lunes = turno
        elif count == 1:
            martes = turno
        elif count == 2:
            miercoles = turno
        elif count == 3:
            jueves = turno
        elif count == 4:
            viernes = turno
        elif count == 5:
            sabado = turno
        elif count == 6:
            domingo = turno

        from datetime import datetime,timedelta
        fecha_py = datetime.strptime(fecha, '%Y%m%d')

        dias = timedelta(days=1)
        fecha_py = fecha_py+dias
        ano = fecha_py.year
        mes = fecha_py.month
        dia = fecha_py.day

        if dia < 10:
            dia = "0" + str(dia)
        else:
            dia = str(dia)

        if mes < 10:
            mes = "0" + str(mes)
        else:
            mes = str(mes)

        fecha = str(ano) + mes + dia

        count = count + 1


    dict = {'nombre': nombre, 'lunes': lunes, 'martes': martes, 'miercoles': miercoles, 'jueves': jueves, 'viernes': viernes, 'sabado': sabado, 'domingo': domingo, 'comentario': comentario }
    return HttpResponse(json.dumps(dict), content_type="application/json")

@login_required    
def repetir_semana_anterior(request):

    mensaje = ''

    if request.method == 'GET':
        pass
    elif request.method == 'POST':

        try:
            id_empleado = request.POST.get('id_empleado')
            fecha_int   = request.POST.get('fecha_int')

            from datetime import datetime,timedelta
            fecha_ac = datetime.strptime(fecha_int, '%Y%m%d')

            dias = timedelta(days=7)
            fecha_py = fecha_ac - dias

            count = 0
            while (count < 7):

                ano = fecha_py.year
                mes = fecha_py.month
                dia = fecha_py.day

                if dia < 10:
                    dia = "0" + str(dia)
                else:
                    dia = str(dia)

                if mes < 10:
                    mes = "0" + str(mes)
                else:
                    mes = str(mes)

                fecha = str(ano) + mes + dia

                empleado = Empleado.objects.get(id=int(id_empleado))
                horario_ori = empleado.horariosempleados_set.filter(fecha=fecha)
                if len(horario_ori) > 0:
                    horario_ori = horario_ori[0]
                    horario = empleado.horariosempleados_set.filter(fecha=fecha_int)
                    if len(horario) > 0:
                        horario = horario[0]
                    else:
                        horario = HorariosEmpleados()
                        horario.empleado = empleado

                    horario.fecha = fecha_int
                    horario.turno = horario_ori.turno
                    horario.comentario = horario_ori.comentario
                    horario.save()

                dias = timedelta(days=1)
                fecha_ac = fecha_ac + dias
                fecha_py = fecha_py + dias

                ano = fecha_ac.year
                mes = fecha_ac.month
                dia = fecha_ac.day

                if dia < 10:
                    dia = "0" + str(dia)
                else:
                    dia = str(dia)

                if mes < 10:
                    mes = "0" + str(mes)
                else:
                    mes = str(mes)

                fecha_int = str(ano) + mes + dia
                count = count + 1

        except Exception as e:
            mensaje = str(e)

    dict = {'error': mensaje}
    return HttpResponse(json.dumps(dict), content_type="application/json")

@login_required    
def guardar_horario(request):
    mensaje = ''

    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        try:
            id_empleado   = request.POST.get('id_empleado')
            fecha_inicio  = request.POST.get('fecha_inicio')
            lunes         = request.POST.get('lunes')
            martes        = request.POST.get('martes')
            miercoles     = request.POST.get('miercoles')
            jueves        = request.POST.get('jueves')
            viernes       = request.POST.get('viernes')
            sabado        = request.POST.get('sabado')
            domingo       = request.POST.get('domingo')
            ########## 25/10 ############
            comentario    = request.POST.get('comentario')
            #############################

            count = 0
            while (count < 7):

                empleado = Empleado.objects.get(id=int(id_empleado))
                horario = empleado.horariosempleados_set.filter(fecha=fecha_inicio)
                if len(horario) > 0:
                    horario = horario[0]
                else:
                    horario = HorariosEmpleados()

                horario.empleado = empleado
                horario.fecha    = fecha_inicio
                if count == 0:
                    horario.turno = lunes
                elif count == 1:
                    horario.turno = martes
                elif count == 2:
                    horario.turno = miercoles
                elif count == 3:
                    horario.turno = jueves
                elif count == 4:
                    horario.turno = viernes
                elif count == 5:
                    horario.turno = sabado
                elif count == 6:
                    horario.turno = domingo
                ###### 25/10 ######
                horario.comentario = comentario
                ###################
                horario.save()

                from datetime import datetime,timedelta
                fecha_py = datetime.strptime(fecha_inicio, '%Y%m%d')

                dias = timedelta(days=1)
                fecha_py = fecha_py+dias
                ano = fecha_py.year
                mes = fecha_py.month
                dia = fecha_py.day

                if dia < 10:
                    dia = "0" + str(dia)
                else:
                    dia = str(dia)

                if mes < 10:
                    mes = "0" + str(mes)
                else:
                    mes = str(mes)

                fecha_inicio = str(ano) + mes + dia

                count = count + 1


        except Exception as e:
            mensaje = str(e)

    dict = {'error': mensaje}
    return HttpResponse(json.dumps(dict), content_type="application/json")


@login_required    
def reporte_facturacion(request):
    mensaje = ''
    id_producto = ''
    productos = Producto.objects.filter(activo=True)

    empl_list = []
    empl_dict = {}
    from datetime import date
    d = date.today()
    fecha_desde = str(d.year) + '-' + str(d.month) + '-' + str(d.day-2)
    fecha_hasta = str(d.year) + '-' + str(d.month)+ '-' + str(d.day-2)

    total_diario = 0
    total_mensual = 0

    empleados = Empleado.objects.filter(activo=True)
    for e in empleados:
        empl_dict = {}
        empl_dict['nombre'] = e.nombre + ' ' + e.apellido
        empl_dict['especialidad'] = e.especialidad.nombre
        empl_dict['total_diario'] = e.dame_facturacion_diaria()
        empl_dict['total_mensual'] = e.dame_facturacion_mensual()
        total_diario = total_diario + empl_dict['total_diario']
        total_mensual = total_mensual + empl_dict['total_mensual']
        empl_list.append(empl_dict)

    context = {'mensaje': mensaje, 'productos': productos, 'id_producto': id_producto, 'total_mensual':total_mensual, 'total_diario':total_diario, 'empl_list': empl_list, 'empleados': empleados}
    return render(request, 'reporte_facturacion.html', context)

@login_required    
def imprimir_ticket(request):
    mensaje = ''
    fecha = str(datetime.datetime.now().day) + '/' + str(datetime.datetime.now().month) + '/' + str(datetime.datetime.now().year) 
    hora = str(datetime.datetime.now().hour) + ':' + str(datetime.datetime.now().minute) + ':' + str(datetime.datetime.now().second)
    id_cliente = request.GET.get('id_cliente')
    cliente = Cliente.objects.get(id=id_cliente)
    context = {'mensaje': mensaje, 'cliente': cliente, 'fecha': fecha, 'hora': hora}
    return render(request, 'imprimir_ticket.html', context)




#metodo privado, no pertenece a una url
def dame_fechas_reportes(fecha_int, semana):
    
    from datetime import timedelta
    
    if fecha_int == '':
        import datetime
        hoy = datetime.datetime.now()
    else:
        from datetime import datetime
        fecha_py = datetime.strptime(fecha_int, '%Y%m%d')
        dias = timedelta(days=7)
        if semana == 'siguiente':
            hoy = fecha_py + dias
        elif semana == 'anterior':
            hoy = fecha_py - dias
        else:
            hoy = fecha_py

    nombre_dia = hoy.strftime("%A")

    if nombre_dia == "Monday":
        lunes = hoy
    elif nombre_dia == "Tuesday":
        dias = timedelta(days=-1)
        lunes = hoy + dias
    elif nombre_dia == "Wednesday":
        dias = timedelta(days=-2)
        lunes = hoy + dias
    elif nombre_dia == "Thursday":
        dias = timedelta(days=-3)
        lunes = hoy + dias
    elif nombre_dia == "Friday":
        dias = timedelta(days=-4)
        lunes = hoy + dias
    elif nombre_dia == "Saturday":
        dias = timedelta(days=-5)
        lunes = hoy + dias
    elif nombre_dia == "Sunday":
        dias = timedelta(days=-6)
        lunes = hoy + dias

    dias = timedelta(days=6)
    fecha_desde = str(lunes.day) + '/' + str(lunes.month) + '/' + str(lunes.year)
    domingo = lunes + dias
    fecha_hasta = str(domingo.day) + '/' + str(domingo.month) + '/' + str(domingo.year)

    if lunes.day < 10:
        dia = '0' + str(lunes.day)
    else:
        dia = str(lunes.day)

    if lunes.month < 10:
        mes = '0' + str(lunes.month)
    else:
        mes = str(lunes.month)

    ano = str(lunes.year)

    fecha_int = ano + mes + dia

    return fecha_desde, fecha_hasta, fecha_int
