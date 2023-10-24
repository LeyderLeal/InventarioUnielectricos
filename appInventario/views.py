from django.forms import IntegerField
from django.shortcuts import render, redirect
from django.db import Error, transaction
from appInventario.models import *
from django.contrib.auth.models import Group
from django.urls import reverse
import random 
import string
from django.http import FileResponse
import json
#enviar correo
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
import threading #hilos envio de correo
from smtplib import SMTPException
#Funcion login 
from django.contrib.auth import login,authenticate
from django.contrib import auth
from django.conf import settings
import urllib
import urllib.parse
import urllib.request
import base64
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.views.decorators.csrf import  csrf_exempt
from decimal import Decimal
from django.shortcuts import get_object_or_404

from django.contrib import messages
import sweetify

from reportlab.lib.pagesizes import letter, landscape, portrait
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from xhtml2pdf import pisa
from reportlab.lib.colors import HexColor
from io import BytesIO

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from appInventario.serializers import *
from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import render

from django.core.exceptions import ObjectDoesNotExist


from django.db.models import Q,Sum, Max, Count, Avg, Func, ExpressionWrapper, IntegerField,F
import matplotlib 
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import numpy as np
import os
from reportlab.lib.styles import ParagraphStyle
from django.views.defaults import page_not_found

import re
# Create your views here.


def inicioSesion(request, mensaje = ""):
    retorno ={"mensaje": mensaje}
    return render(request,"frmInicioSesion.html", retorno)

def es_empleado(user):
    return user.groups.filter(name='Empleado').exists()
def es_administrador(user):
    return user.groups.filter(name='Administrador').exists()


@login_required(login_url='/')
@user_passes_test(es_administrador, login_url='/inicioA/')

def inicioAdministrador(request):
    productos = Producto.objects.all().order_by('-fechaHoraActualizacion')
   
    roles = Group.objects.all()
    retorno = {"listaProductos":productos, "roles":roles}
    if request.user.is_authenticated:
        return render(request,"Administrador/inicioA.html", retorno)
    else:
        retorno="Debe ingresar con sus credenciales"
        return redirect(f"loginX/{retorno}")



@login_required(login_url='/')
@user_passes_test(es_empleado, login_url='/inicioE/')
def inicioEmpleado(request):
    if request.user.is_authenticated:
        return render(request,"Empleado/inicioE.html")
    else:
        retorno="Debe ingresar con sus credenciales"
        return redirect(f"loginX/{retorno}")



@login_required(login_url='/')
@user_passes_test(es_empleado, login_url='/inicioE/')
def vistaPerfil(request):
    try:
        usuario = request.user
        mensaje = ""
    except Error as error:
        mensaje = f"problemas al mostrar el perfil {error}"
    retorno = {"mensaje":mensaje,"usuario":usuario}
    return render (request, "Empleado/perfil.html",retorno)



@login_required(login_url='/')
@user_passes_test(es_administrador, login_url='/inicioA/')
def listaUsuario(request):
    try:
        usuarios = User.objects.all().order_by('-fechaHoraActualizacion')
        mensaje=""
    except Error as error:
        mensaje = f"problemas al listar Usuarios {error}"
    retorno = {"mensaje":mensaje,"listaUsuarios":usuarios}
    return render (request, "Administrador/listarUsuarios.html",retorno)



@login_required(login_url='/')
def vistaRegistrarUsuario(request):
    roles = Group.objects.all()
    retorno = {"roles":roles}
    return render(request,"Administrador/frmRegistrarUsuario.html", retorno)



@login_required(login_url='/')
def registrarUsuario(request):
    try:
        nombres = request.POST["txtNombres"]
        apellidos = request.POST["txtApellidos"]
        nomUsuario = request.POST["txtnomUsuario"]
        correo = request.POST["txtCorreo"]
        idRol = int(request.POST["cbRol"])
        
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not nombres or not apellidos or not nomUsuario or not correo or not re.match(email_pattern, correo) or not idRol:
            return JsonResponse({'estado': False, 'mensaje': 'Campos requeridos incompletos o dirección de correo inválida.'})
        
        with transaction.atomic():
            user=User(username=nomUsuario, first_name=nombres, last_name=apellidos, email=correo)
            user.save()
                
            rol=Group.objects.get(pk=idRol)
            user.groups.add(rol)
            if rol.name == "Administrador":
                user.is_staff = True
            user.save()

            passwordGenerado= generarPassword()
            print(f"password{passwordGenerado}")
            user.set_password(passwordGenerado)
            user.save()
            estado = True
            mensaje = "Registrado Correctamente"
                
            asunto='Registro Sistema Inventario UNIELECTRICOS-NEIVA'
            mensaje=f'Cordial Saludo, <b>{user.first_name} {user.last_name}</b>, nos permitimos \
                informarle que usted ha sido registrado en el sistema de Gestión de Inventario \
                de UNIELECTRICOS-NEIVA. \
                Nos permitimos enviarle las credenciales de Ingreso a nuestro sistema.<br>\
                <br><b>Username: </b>{user.username}\
                <br><b>Password: </b>{passwordGenerado}\
                <br><b>Lo invitamos a ingresar a nuestro sistema en la url:\
                https://unielectricos.pythonanywhere.com </b><br><br>\
                <br><br>\
                <p>Atentamente:<br>\
                <span style="font-weight: bold;">Administración - Unielectricos</span><br>\
                <span>Telefono: 8720547</span><br>\
                <span>unielectricos@gmail.com</span></p>\
                <br><br><img src="media/iconoBlanco2.png" alt="Unielectricos" />\
                <br><br>'
            
                    
            thread=threading.Thread(target=enviarCorreo, args=(asunto, mensaje, user.email))
            thread.start()
            
            mensaje="Usuario registrado correctamente"
            estado = True
            
            return JsonResponse({'estado': True, 'mensaje': mensaje})
            return redirect('listaUsuario')
        
    except Exception as e:
            transaction.rollback()
            mensaje = str(e)
            return JsonResponse({'estado': False, 'mensaje': mensaje})
    
    

@login_required(login_url='/')
def editarUsuario(request, id):
    try:
        usuario = User.objects.get(id=id)
        mensaje=""
    except Error as error:
         mensaje = f"Problemas al editar Usuario{error}"
    retorno = {"mensaje": mensaje, "usuario":usuario}
    if request.user.groups.filter(name='Administrador').exists():
        return render(request, "Administrador/frmEditarUsuario.html", retorno)
    else:
        return render(request, 'Empleado/frmEditarUsuario.html', retorno)



@login_required(login_url='/')
def actualizarUsuario(request):
    try:
        idUsuario = int(request.POST.get("idUsuario"))
        nombre = request.POST.get("txtNombre")
        apellido = request.POST.get("txtApellido")
        username = request.POST.get("txtUsername")
        correo = request.POST.get("txtCorreo")

        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not nombre or not apellido or not username or not correo or not re.match(email_pattern, correo):
            return JsonResponse({'estado': False, 'mensaje': 'Campos requeridos incompletos o dirección de correo inválida.'})

        with transaction.atomic():
            usuario = User.objects.get(id=idUsuario)
            usuario.first_name = nombre
            usuario.last_name = apellido
            usuario.username = username
            usuario.email = correo
            usuario.save()
            
            estado = True
            mensaje = "Usuario actualizado correctamente"
            
            if request.user.groups.filter(name='Administrador').exists():
                return JsonResponse({'estado': True, 'mensaje': mensaje})
                return redirect("/listaUsuario/")
            else:
                return JsonResponse({'estado': True, 'mensaje': mensaje})
                return redirect("/perfil/")
        
    except Exception as e:
        transaction.rollback()
        mensaje = str(e)
        return JsonResponse({'estado': False, 'mensaje': mensaje})
    


@login_required(login_url='/')
def suspendeUsuario(request, user_id, mensaje):
    try:
        user_id = user_id
        estado = mensaje
        print(estado)
        with transaction.atomic():
            user = User.objects.get(pk = user_id)
            user.userEstado = estado
            user.save()
            retorno = {
                "mensaje": "Estado Actualizado Correctamente",
                "estado": True
            }
            return JsonResponse(retorno)
        
    except Exception as er:
        transaction.rollback()
        retorno = {
                "mensaje": "Error al Actualizar el Estado",
                "estado": False
        }
        return JsonResponse(retorno)
        
        


@login_required(login_url='/')
@csrf_exempt  # Esto es necesario si no estás manejando CSRF en tu frontend
def activaUsuario(request, user_id, mensaje):
    try:
        user_id = user_id
        estado = mensaje
        print(estado)
        # Obtén el usuario por su ID
        user = User.objects.get(pk=user_id)
        
        # Actualiza el estado del usuario según el valor recibido ('Activo' o 'Inactivo')
        user.userEstado = estado
        user.save()
        
        retorno = {
            "mensaje": "Estado Actualizado Correctamente",
            "estado": True
        }
        
        return JsonResponse(retorno)
        
    except User.DoesNotExist:
        retorno = {
            "mensaje": "Usuario no encontrado",
            "estado": False
        }
    except Exception as e:
        retorno = {
            "mensaje": "Error al Actualizar el Estado",
            "estado": False
        }
        
    return JsonResponse(retorno)



@login_required(login_url='/')
def enviarCorreo(asunto=None, contenido=None, destinatario=None):
    remitente = settings.EMAIL_HOST_USER
    try:
        correo = EmailMultiAlternatives(asunto, '', remitente, [destinatario])
        correo.attach_alternative(contenido, 'text/html')
        correo.send(fail_silently=True)
    except SMTPException as error:
        print(error)



@login_required(login_url='/')       
def generarPassword():
    longitud = 10
    caracteres = string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation
    password = ''
    for i in range(longitud):
        password += ''.join(random.choice(caracteres))
    return password
        
        

@login_required  # Asegura que el usuario esté autenticado para acceder a esta vista
def actualizarContra(request):
    if request.method == 'POST':
        try:
            user_id = request.POST.get('idUsuario')
            contraActual = request.POST.get('contraActual')
            nuevaContra = request.POST.get('nuevaContra')
            confirmarContra = request.POST.get('confirmarContra')

            user = User.objects.get(id=user_id)

            # Valida las contraseñas
            if not user.check_password(contraActual):
                return JsonResponse({'estado': False, 'mensaje': 'Contraseña actual incorrecta'})

            
            if not nuevaContra:
                return JsonResponse({'estado': False, 'mensaje': 'La nueva contraseña no puede estar vacía'})
            elif nuevaContra != confirmarContra:
                return JsonResponse({'estado': False, 'mensaje': 'Las contraseñas no coinciden'})

            # Cambia la contraseña y guarda el usuario
            user.set_password(nuevaContra)
            user.save()
            
            asunto='Registro Sistema Inventario UNIELECTRICOS-NEIVA'
                
            mensaje=f'Cordial Saludo, <b>{user.first_name} {user.last_name}</b>, nos permitimos \
                informarle que usted ha realizado un cambio en su contraseña registrada en el sistema de Gestión de Inventario \
                de UNIELECTRICOS-NEIVA. \
                Nos permitimos enviarle las actuales credenciales de ingreso a nuestro sistema.<br>\
                <br><b>Username: </b>{user.username}\
                <br><b>Password: </b>{nuevaContra}\
                <br><b>Lo invitamos a ingresar a nuestro sistema en la url:\
                https://unielectricos.pythonanywhere.com </b>\
                <p>Atentamente:<br>\
                <span style="font-weight: bold;">Administración - Unielectricos</span><br>\
                <span>Telefono: 8720547</span><br>\
                <span>unielectricos@gmail.com</span></p>\
                <br><br><img src="media/iconoBlanco2.png" alt="Unielectricos" />\
                <br><br>'
                
            thread=threading.Thread(target=enviarCorreo, args=(asunto, mensaje, user.email))
            thread.start()
            
            mensaje="Contraseña actualizada correctamente"
            estado = True
            
            return JsonResponse({'estado': estado, 'mensaje': mensaje})
        
        except User.DoesNotExist:
            mensaje = "El usuario no existe"
        except Exception as error:
            mensaje = f"Problemas al actualizar la Contraseña: {error}"
    else:
        mensaje = "Método no permitido para la actualización"
        
    return JsonResponse({'estado': False, 'mensaje': mensaje})
    


def vistaRecuperarContra(request):
    return render(request, "frmRecuperarContra.html")



def recuperarContra(request):
    if request.method == 'POST':
        try:
            correo = request.POST.get('Email')
            # Buscar usuarios por correo electrónico
            usuarios = User.objects.filter(email=correo)
            
            if usuarios.exists():
                for usuario in usuarios:
                    
                    passwordGenerado= generarPassword()
                    print(f"password{passwordGenerado}")
                    usuario.set_password(passwordGenerado)
                    usuario.save()
                    
                    asunto = 'Recuperación Sistema Inventario UNIELECTRICOS-NEIVA'
                
                    mensaje = f'Cordial Saludo, <b>{usuario.first_name} {usuario.last_name}</b>. \
                        Nos permitimos enviarle las actuales credenciales de ingreso a nuestro sistema.<br>\
                        <br><b>Username: </b>{usuario.username}\
                        <br><b>Password: </b>{passwordGenerado}\
                        <br><b>Lo invitamos a ingresar a nuestro sistema y cambiar su contraseña en la url:\
                       <br><b>Lo invitamos a ingresar a nuestro sistema en la url:\
                        https://unielectricos.pythonanywhere.com </b> <br><br>    \
                        <p>Atentamente:<br>\
                        <span style="font-weight: bold;">Administración - Unielectricos</span><br>\
                        <span>Telefono: 8720547</span><br>\
                        <span>unielectricos@gmail.com</span></p>\
                        <br><br><img src="media/iconoBlanco2.png" alt="Unielectricos" />\
                        <br><br>'  
                
                    thread = threading.Thread(target=enviarCorreo, args=(asunto, mensaje, usuario.email))
                    thread.start()
                
                mensaje = "Correo(s) enviado(s) correctamente"
                estado = True
                sweetify.success(request, mensaje)
            else:
                mensaje = "El correo no existe en la base de datos"
                estado = False
                sweetify.error(request, mensaje)
            
        except Exception as error:
            mensaje = f"Problemas al enviar el Correo: {error}"
            estado = False
            sweetify.error(request, mensaje)

        return JsonResponse({'estado': estado, 'mensaje': mensaje})
    
    else:
        mensaje = "Método no permitido para la Recuperación"
        sweetify.error(request, mensaje)
        return JsonResponse({'estado': False, 'mensaje': mensaje})



@csrf_exempt
def loginX(request):
    estado = "Activo"
    mensaje = "Debes ingresar tus Credenciales"
    
    if request.method == "POST":
        recaptcha_response = request.POST.get('g-recaptcha-response')
        
        # Verificar reCAPTCHA v3
        url = 'https://www.google.com/recaptcha/api/siteverify'
        data = {
            'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response,
        }
        
        try:
            response = urllib.request.urlopen(url, urllib.parse.urlencode(data).encode())
            result = json.loads(response.read().decode())
            
            if result['success']:
                username = request.POST["txtUsername"]
                password = request.POST["txtPassword"]
                user = authenticate(username=username, password=password)
                
                if user is not None:
                    # Registrar la variable de sesión
                    if user.userEstado == estado:
                
                        auth.login(request, user)
                        if user.groups.filter(name='Administrador').exists():
                            return redirect('/inicioA')
                        elif user.groups.filter(name='Empleado').exists():
                            return redirect('/inicioE')
                        else:
                            return redirect(f'/inicio/')
                    else:
                        mensaje = "Cuenta Inactiva"
                        return redirect(f'/inicio/{mensaje}')
                else:    
                    
                    mensaje = "Usuario o Contraseña Incorrectas"
                    return redirect(f'/inicio/{mensaje}')
            
        except Exception as e:
            transaction.rollback()
            print(e)
    return render(request, "frmInicioSesion.html", {"mensaje": mensaje, "estado": estado})



@login_required(login_url='/')
def listaProveedor(request):
    try:
        proveedor = Proveedor.objects.all().order_by('-fechaHoraActualizacion')
        mensaje=""
        retorno = {"mensaje": mensaje, "listaProveedor": proveedor}
        if request.user.groups.filter(name='Administrador').exists():
            return render(request, "Administrador/listarProveedor.html",retorno)
        else:
            return render(request, "Empleado/listarProveedor.html",retorno)
    except Error as error:
        mensaje = f"problemas al listar unidades {error}"
    retorno = {"mensaje": mensaje, "listaProveedor": proveedor}
    return render (request, "Administrador/listarProveedor.html",retorno)



@login_required(login_url='/')
def vistaRegistrarProveedor(request):
    tipoProveedor = [
        ('Persona Jurídica', 'Persona Jurídica'),
        ('Persona Natural', 'Persona Natural'),
    ]
    retorno = {"tipoProveedor": tipoProveedor}
    
    if request.user.groups.filter(name='Administrador').exists():
        return render(request, "Administrador/frmRegistrarProveedor.html", retorno)
    else:
        return render(request, "Empleado/frmRegistrarProveedor.html", retorno)
    


@login_required(login_url='/')
def registrarProveedor(request):
    try:
        tipo = request.POST["tipoProveedor"]
        identificacion = request.POST["txtIdentificacion"]
        nombre = request.POST["txtNombre"]
        telefono = request.POST.get("txtCelular", None)

        if not tipo or not identificacion or not nombre or not telefono :
            return JsonResponse({'estado': False, 'mensaje': 'Campos requeridos incompletos.'})

        with transaction.atomic():
            proveedor = Proveedor(
                proTipo=tipo,
                proIdentificacion=identificacion,
                proNombre=nombre,
                proTelefono=telefono
            )
            proveedor.save()
            mensaje = "Proveedor Agregado Correctamente"
            estado = True
            retorno = {"mensaje": mensaje}
            
            return JsonResponse({'estado': True, 'mensaje': mensaje})


    except Exception as error:
        transaction.rollback()
        mensaje = str(error)
        return JsonResponse({'estado': False, 'mensaje': mensaje})

    tipoProveedor = [
        ('Persona Jurídica', 'Persona Jurídica'),
        ('Persona Natural', 'Persona Natural'),
    ]
    retorno = {"mensaje": mensaje, "tipoProveedor": tipoProveedor}
    return render(request, "Administrador/frmRegistrarProveedor.html", retorno)



@login_required(login_url='/')
def editarProveedor(request, id):
    try:
        tipoProveedor = [
        ('Persona Jurídica'),
        ('Persona Natural'),]
        proveedor = Proveedor.objects.get(id=id)
        mensaje=""
    except Error as error:
         mensaje = f"Problemas al editar proveedor{error}"
    retorno = {"mensaje": mensaje, "proveedor":proveedor, "tipoProveedor":tipoProveedor}
    return render(request, "Administrador/frmEditarProveedor.html", retorno)
        
        

@login_required(login_url='/')
def actualizarProveedor(request):
    if request.method == 'POST':
        try:
            idProveedor = int(request.POST.get("idProveedor"))
            tipo = request.POST.get("cbtipoProveedor")
            identificacion = request.POST.get("txtIdentificacion")
            nombre = request.POST.get("txtNombre")
            telefono = request.POST.get("txtCelular", None)
            
            estado = False
            proveedor = Proveedor.objects.get(id=idProveedor)
            proveedor.proTipo = tipo
            proveedor.proIdentificacion = identificacion
            proveedor.proNombre = nombre
            proveedor.proTelefono = telefono
            
            proveedor.save()
            mensaje = "Proveedor actualizado correctamente"
            estado = True
            return redirect("/listaProveedor/")
       
        except Proveedor.DoesNotExist as error:
            mensaje = f"Proveedor no encontrado: {error}"
        except Error as error:
            mensaje = f"Problemas al actualizar el proveedor: {error}"
    else:
        mensaje = "Método no permitido para la actualización"
        estado = False

    tipo = Proveedor.objects.all()
    retorno = {"mensaje": mensaje, "tipoProveedor": tipo, "estado": estado}
    return render(request, "Administrador/frmEditarProveedor.html", retorno)



@login_required(login_url='/')
def eliminarProveedor(request, proIdentificacion):
    estado= False
    mensaje = ""
    try:
        
        proveedor = Proveedor.objects.get(proIdentificacion=proIdentificacion)
        proveedor.delete()
        mensaje = "Proveedor eliminado correctamente"
        estado = True
        
    except Proveedor.DoesNotExist:
        mensaje = f"El proveedor no existe."
       
    except Exception as e:
         mensaje = "El proveedor no se puede eliminar"
         
    response_data = {"estado": estado, "mensaje": mensaje}
    return JsonResponse(response_data)



@login_required(login_url='/')
def listaProducto(request):
    productos = Producto.objects.all().order_by('-fechaHoraActualizacion')
    retorno = {"listaProductos":productos}
    if request.user.groups.filter(name='Administrador').exists():
        return render(request, "Administrador/listarProductos.html", retorno)
    else:
        return render(request, "Empleado/listarProductos.html", retorno)



@login_required(login_url='/')
def vistaRegistrarProducto(request):
    unidadesMedida = UnidadMedida.objects.all()
    marcas = Marca.objects.all()
    retorno = {"unidadesMedida": unidadesMedida, "marcas": marcas}
    return render(request,"Administrador/frmRegistrarProducto.html", retorno)



@login_required(login_url='/')
def registrarProducto(request):
    try:
        nombre = request.POST["txtNombre"]
        precio = int(request.POST["txtPrecio"])
        marca = request.POST.get("txtMarca")
        unidadMedida = request.POST.get("txtUnidadMedida")
        descripcion = request.POST.get("txtDescripcion", None)
        archivo = request.FILES.get("fileFoto")

        if not nombre or not precio or not marca or not unidadMedida:
            return JsonResponse({'estado': False, 'mensaje': 'Campos requeridos incompletos.'})
        
        with transaction.atomic():
            # Obtener las instancias de Marca y UnidadMedida
            marca = get_object_or_404(Marca, id=marca)
            unidadMedida = get_object_or_404(UnidadMedida, id=unidadMedida)

            cantidad = Producto.objects.all().count()
            nombre_abreviado = nombre[:3]
            codigoProducto = nombre_abreviado.upper() + str(cantidad + 1).rjust(4, '0')
            cantidad = 0
            # Crear el producto
            producto = Producto(
                proCodigo=codigoProducto,
                proNombre=nombre,
                proDescripcion=descripcion,
                proMarca=marca,
                proPrecio=precio,
                proFoto=archivo,
                proUnidadMedida=unidadMedida,
                proCantidad=cantidad
            )

            # Guardar el producto en la base de datos
            producto.save()

            estado = True
            mensaje = f"Producto registrado satisfactoriamente con el código {codigoProducto}"

            return JsonResponse({'estado': True, 'mensaje': mensaje})
            return redirect('listaProducto')
        
    except Error as error:
        transaction.rollback()
        mensaje = str(error)
        return JsonResponse({'estado': False, 'mensaje': mensaje})

    

@login_required(login_url='/')
def editarProducto(request, id):
    try:
        producto = Producto.objects.get(id=id)
        unidadM = UnidadMedida.objects.all()
        marca = Marca.objects.all()
        mensaje=""
    except Error as error:
        mensaje = f"Problemas al editar el Producto{error}"
    retorno = {"mensaje": mensaje, "producto": producto, "unidadMedida": unidadM, "marcas":marca}
    return render(request, "Administrador/frmEditarProducto.html", retorno)



@login_required(login_url='/')
def actualizarProducto(request):
    
    idProducto = int(request.POST["idProducto"])
    nombre = request.POST["txtNombre"]
    idUnidadMedida = int(request.POST["cbUnidadMedida"])
    precio = int(request.POST["txtPrecio"])
    idMarca = int(request.POST["cbMarca"])
    descripcion = request.POST["txtDescripcion"]
    archivo = request.FILES.get("fileFoto", False)
    try:
        estado = False
        unidadM = UnidadMedida.objects.get(id=idUnidadMedida)
        marca = Marca.objects.get(id = idMarca)
        #actualizar el producto. PRIMERO SE CONSULTA
        producto = Producto.objects.get(id=idProducto)
        producto.proNombre=nombre
        producto.proUnidadMedida=unidadM
        producto.proPrecio=precio
        producto.proMarca=marca
        producto.proDescripcion=descripcion
        #si el campo de foto tiene datos actualiza foto
        if(archivo):
            producto.proFoto = archivo
        else:
            producto.proFoto = producto.proFoto
        producto.save()
        mensaje = "Producto actualizado correctamente"
        estado=True
        return redirect("/listaProducto/")

    except Error as error:
        mensaje = f"Problemas al de actualizar el producto {error}"
    unidadM = UnidadMedida.objects.all()
    marca = Marca.objects.all()
    retorno = {"mensaje":mensaje, "unidadMedida":unidadM, "marcas": marca, "producto":producto, "estado": estado}
    return render(request,"Administrador/frmEditarProducto.html", retorno)



@login_required(login_url='/')
def eliminarProducto(request, proCodigo):
    estado = False
    mensaje = ""
    try:
        producto = Producto.objects.get(proCodigo=proCodigo)
        producto.proFoto.storage.delete(producto.proFoto.name)
        producto.delete()
        mensaje = "Producto Eliminado!"
        estado = True
    except ObjectDoesNotExist as error:
        mensaje = f"El producto con código {proCodigo} no existe."
    except Exception as error:
        mensaje = f"Problemas al eliminar el producto: {error}"

    response_data = {"estado": estado, "mensaje": mensaje}
    return JsonResponse(response_data)



@login_required(login_url='/')
@user_passes_test(es_administrador, login_url='/inicioA/')
def listaCompra(request):
    compras = Compra.objects.all().order_by('-fechaHoraActualizacion')
    productos = Producto.objects.all()
    retorno ={'compras': compras, 'productos': productos}
    return render(request, 'Administrador/listarCompras.html', retorno)



@login_required(login_url='/')
@user_passes_test(es_administrador, login_url='/inicioA/')
def vistaRegistrarCompra(request):
    proveedores = Proveedor.objects.all()
    usuario = request.user
    productos = Producto.objects.all()
    retorno = {'proveedores': proveedores, 'usuario': usuario, 'productos': productos}
    return render(request, 'Administrador/frmRegistrarCompra.html', retorno)



@login_required(login_url='/')
@user_passes_test(es_administrador, login_url='/inicioA/')
def registrarCompra(request):
    proveedores = Proveedor.objects.all()
    usuario = request.user
    productos = Producto.objects.all()
    
    if request.method == "POST":
        codigoCompra = request.POST.get('codigoCompra')
        idProveedor = int(request.POST.get('proveedor'))
        recibidoPor = int(request.POST.get('recibidoPor'))
        observaciones = request.POST.get('observaciones')
        
        if not idProveedor or not recibidoPor:
            return JsonResponse({'estado': False, 'mensaje': 'Faltan campos requeridos.'})
        
        proveedor = Proveedor.objects.get(pk=idProveedor)
        usuarioRecibe = User.objects.get(pk=recibidoPor)
        productosComprados = json.loads(request.POST.get('productosComprados'))
        
        if not productosComprados:
            return JsonResponse({'estado': False, 'mensaje': 'No se registraron productos en la compra.'})
        precioTotal = sum(float(producto['precioAcumulado']) if producto['precioAcumulado'] else 0 for producto in productosComprados)
    
        with transaction.atomic():
                # Guardar la instancia de Compra con el precioTotal calculado
                compra = Compra.objects.create(
                    comUsuarioRecibe=usuarioRecibe,
                    comProveedor=proveedor,
                    comObservaciones=observaciones,
                    comPrecioTotal=precioTotal,
                )

                for productoComprado in productosComprados:
                    idProducto = int(productoComprado['codigo'])
                    cantidad = int(productoComprado['cantidad'])
                    precio = float(productoComprado['precio'])
                    precioAcumulado = float(productoComprado['precioAcumulado'])
                    producto = Producto.objects.get(pk=idProducto)
                
                    detalleCompraObj = DetalleCompra(
                        detCompra=compra,
                        detProducto=producto,
                        detCantidad=cantidad,
                        detPrecioUnitario=precio,
                        detPrecioAcumulativo=precioAcumulado,
                    )
                    
                    detalleCompraObj.save()
                    
                    producto.proCompra += cantidad
                    producto.proCantidad += cantidad
                    producto.save()
                
                codigoCompra = compra.pk
                
        return JsonResponse({"estado": True, "mensaje": f'Compra realizada y registrada satisfactoriamente con el código {codigoCompra}.'}, status=200)
    
    retorno = {'proveedores': proveedores, 'usuario': usuario, 'productos': productos}
    return render(request, 'Administrador/frmRegistrarCompra.html', retorno)



@login_required(login_url='/')
def generar_pdf_compra(request, compra_id):
    try:
        # Obtener la compra por su ID
        compra = Compra.objects.get(pk=compra_id)
    except Compra.DoesNotExist:
        # Puedes manejar aquí el caso en que la compra no existe
        return HttpResponse("La compra no existe.")

    # Generar el nombre del archivo PDF usando el código de compra
    nombre_archivo = f"compra_{compra.comCodigo}.pdf"

    # Configurar la respuesta del PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{nombre_archivo}"'
 
    # Crear el documento PDF
    doc = SimpleDocTemplate(response, pagesize=portrait (letter), title="Factura de la Compra.PDF")

    # Crear una lista para almacenar los elementos del PDF
    elementos = []
    
    imagen_path = 'media/iconoBlanco.png'  # Reemplaza con la ruta de tu imagen
    imagen = Image(imagen_path, width=400, height=100)  # Ajusta el ancho y alto según tu preferencia
    elementos.append(imagen)

    # Establecer el estilo del documento
    estilos = getSampleStyleSheet()
    titulo_estilo = estilos['Heading2']
    titulo_estilo.alignment = 1  # Centrar el título
    
    # Agregar el título del PDF
    elementos.append(Paragraph("FACTURA DE COMPRA", titulo_estilo))
    elementos.append(Spacer(1, 10))
    
    # Agregar detalles completos de la compra al PDF
    elementos.append(Paragraph(f"<strong>Código Factura:</strong> {compra.comCodigo}", estilos['Heading3']))
    elementos.append(Paragraph(f"<strong>Proveedor:</strong> {compra.comProveedor.proNombre}", estilos['Normal']))
    elementos.append(Paragraph(f"<strong>Recibido Por:</strong> {compra.comUsuarioRecibe.username}", estilos['Normal']))
    elementos.append(Paragraph(f"<strong>Fecha Entrega:</strong> {compra.fechaHoraCreacion}", estilos['Normal']))
    elementos.append(Paragraph(f"<strong>Observaciones:</strong> {compra.comObservaciones}", estilos['Normal']))
    elementos.append(Spacer(1, 10))

    elementos.append(Spacer(1, 20))
    elementos.append(Paragraph("<u>Detalles de la Compra</u>", estilos['Normal']))
    elementos.append(Spacer(1, 20))
    
    # Agregar detalles de la compra en una tabla
    detalles = [[Paragraph('<strong>Código</strong>', estilos['Normal']), 
                 Paragraph('<strong>Producto</strong>', estilos['Normal']),
                 Paragraph('<strong>Cantidad</strong>', estilos['Normal']),
                 Paragraph('<strong>Precio</strong>', estilos['Normal']),
                 Paragraph('<strong>Precio Acumulado</strong>', estilos['Normal'])]]

    for detalle in compra.detallecompra_set.all():
        detalles.append([
            Paragraph(detalle.detProducto.proCodigo, estilos['Normal']),
            Paragraph(detalle.detProducto.proNombre, estilos['Normal']),
            Paragraph(str(detalle.detCantidad), estilos['Normal']),
            Paragraph(f"${detalle.detPrecioUnitario}", estilos['Normal']),
            Paragraph(f"${detalle.detPrecioAcumulativo}", estilos['Normal']),
        ])

    # Crear la tabla y aplicar el estilo
    colorT = colors.Color(0.9019607843137255, 0.9254901960784314, 0.9607843137254902)
    tabla = Table(detalles, colWidths=[1.2 * inch, 3.2 * inch, 0.8 * inch, 1.2 * inch, 1.5 * inch])
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colorT),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 1), (-1, -1), 1, colors.black)
    ]))

    # Agregar los elementos al PDF
    elementos.append(tabla)

    # Construir el documento PDF
    doc.build(elementos)

    return response



@login_required(login_url='/')
def vistaRegistrarDevProveedor(request, codigoCompra):
    compra = get_object_or_404(Compra, comCodigo=codigoCompra)
    usuario = request.user
    productos = Producto.objects.filter(detallecompra__detCompra=compra)
    
    print("La vista vistaRegistrarDevProveedor se ha ejecutado correctamente.")

    retorno = {'usuario': usuario, 'productos': productos, 'compra': compra, 'codigoCompra': compra.comCodigo}

    if request.user.groups.filter(name='Administrador').exists():
        return render(request,"Administrador/frmRegistrarDevProveedor.html", retorno)
    else:
        return render(request, 'Empleado/frmRegistrarDevProveedor.html', retorno)
    


@login_required(login_url='/')
def registrarDevolucionesPro(request):
    
    if request.method == "POST":
        codigoCompra = request.POST.get('codigoCompra')
        compra = get_object_or_404(Compra, comCodigo=codigoCompra)

        usuario = int(request.POST.get('usuario'))
        
        if not usuario:
            return JsonResponse({'estado': False, 'mensaje': 'Falta el campo "usuario" en los datos POST.'})
        
        devUsuarioDevolucion = User.objects.get(pk=usuario)
        
        productosDevueltos = json.loads(request.POST.get('productosDevueltos'))
        if not productosDevueltos:
            return JsonResponse({'estado': False, 'mensaje': 'No se registraron productos en la Devolución.'})
        
        print(f"productos{productosDevueltos}")
        
        precioTotal = sum(float(producto['precioAcumulado']) if producto['precioAcumulado'] else 0 for producto in productosDevueltos)

        with transaction.atomic():
            # Crea una instancia de Devolucion
            devolucion = DevolucionCompra.objects.create(
                devCompra=compra,
                devUsuarioEntrega=devUsuarioDevolucion,
                devProveedor=compra.comProveedor,
                devPrecioTotal=precioTotal,
            )

            for productoDevuelto in productosDevueltos:
                idProducto = int(productoDevuelto['codigo'])
                cantidadDevuelta = int(productoDevuelto['cantidad'])
                precio = float(productoDevuelto['precio'])
                precioAcumulado = float(productoDevuelto['precioAcumulado'])
                MetodoDevolucion = productoDevuelto['MetodoDevolucion']
                producto = Producto.objects.get(pk=idProducto)
                
                # Crea una instancia de DetalleDevolucion
                detalleDevolucionObj = DetalleDevolucionCompra(
                    devDevolucion=devolucion,
                    devMetodo=MetodoDevolucion,
                    devProducto=producto,
                    devCantidad=cantidadDevuelta,
                    devPrecioUnitario=precio,
                    devPrecioAcumulativo=precioAcumulado,
                )
                
                detalleDevolucionObj.save()
                
                # Realiza la resta en DetalleCompra solo si el método no es "Cambiar por un producto igual"
                if MetodoDevolucion == "Devolver dinero":                
                    detalle_compra = DetalleCompra.objects.get(detCompra=compra, detProducto=producto)
                    detalle_compra.detCantidad -= cantidadDevuelta
                    detalle_compra.detDevueltos += cantidadDevuelta
                    precioUnitario = detalle_compra.detPrecioUnitario
                    detalle_compra.detPrecioAcumulativo -= precioUnitario * cantidadDevuelta
                    detalle_compra.save()

                    # Actualiza la cantidad de producto en la tabla Producto
                    producto.proCantidad -= cantidadDevuelta
                


                producto.save()
                
            # Restablece la cantidad comprada total en la compra si no se eligió "Cambiar por un producto igual"
            if all(producto['MetodoDevolucion'] == "Devolver dinero" for producto in productosDevueltos):
                compra.comPrecioTotal -= precioTotal
                compra.save()
            
            codigoDevolucion = devolucion.pk
            
        return JsonResponse({'estado': True, 'mensaje': f'Devolucion registrada exitosamente con el codigo {codigoDevolucion}.'})
      
    return JsonResponse({'estado': False, 'mensaje': 'La solicitud debe ser de tipo POST.'})



@login_required(login_url='/')
def listaVenta(request):
    ventas = Venta.objects.all().order_by('-fechaHoraActualizacion')
    productos = Producto.objects.all()
    retorno = {'ventas': ventas, 'productos': productos}
    if request.user.groups.filter(name='Administrador').exists():
        return render(request, 'Administrador/listarVentas.html', retorno)
    else:
        return render(request, 'Empleado/listarVentas.html', retorno)        
    


@login_required(login_url='/')
def vistaRegistrarVenta(request):
    usuario = request.user
    productos = Producto.objects.all()
    retorno = {'usuario': usuario, 'productos': productos}

    if request.user.groups.filter(name='Administrador').exists():
        return render(request, 'Administrador/frmRegistrarVenta.html', retorno)
    else:
        return render(request, 'Empleado/frmRegistrarVenta.html', retorno)
        


@login_required(login_url='/')
def registrarVenta(request):
    usuario = request.user
    productos = Producto.objects.all()

    if request.method == "POST":
        codigoVenta = request.POST.get('codigoVenta')
        cliente = request.POST.get('cliente')
        direccion = request.POST.get('txtDireccion', None)
        vendedor = int(request.POST.get('vendedor'))
        observaciones = request.POST.get('observaciones', None)
        
        if not cliente or not vendedor:
            return JsonResponse({'estado': False, 'mensaje': 'Faltan campos requeridos.'})
        
        vendedor = User.objects.get(pk=vendedor)
        productosVendidos = json.loads(request.POST.get('productosVendidos'))
        
        if not productosVendidos:
            return JsonResponse({'estado': False, 'mensaje': 'No se registraron productos en la venta.'})
        precioTotal = sum(float(producto['precioAcumulado']) if producto['precioAcumulado'] else 0 for producto in productosVendidos)

        with transaction.atomic():
            # Guardar la instancia de Venta con el precioTotal calculado
            venta = Venta.objects.create(
                venCodigo=codigoVenta,
                venVendedor=vendedor,
                venCliente=cliente,
                venDireccion=direccion,
                venObservaciones=observaciones,
                venPrecioTotal=precioTotal,
            )

            for productoVendido in productosVendidos:
                idProducto = int(productoVendido['codigo'])
                cantidad = int(productoVendido['cantidad'])
                precio = float(productoVendido['precio'])
                precioAcumulado = float(productoVendido['precioAcumulado'])
                producto = Producto.objects.get(pk=idProducto)
                
                detalleVentaObj = DetalleVenta(
                    detVenta=venta,
                    detProducto=producto,
                    detCantidad=cantidad,
                    detPrecioUnitario=precio,
                    detPrecioAcumulativo=precioAcumulado,
                )
                
                detalleVentaObj.save()
                
                producto.proVenta += cantidad
                producto.proCantidad -= cantidad
                producto.save()
            
            codigoVenta = venta.pk
            
        return JsonResponse({'estado': True, 'mensaje': f'Venta registrada exitosamente con el codigo {codigoVenta}.'})
      
    retorno = {'usuario': usuario, 'productos': productos}
    return render(request, 'Administrador/frmRegistrarVenta.html', retorno)



@login_required(login_url='/')
def generar_pdf_venta(request, venta_id):
    try:
        # Obtener la venta por su ID
        venta = Venta.objects.get(pk=venta_id)
    except Venta.DoesNotExist:
        # Puedes manejar aquí el caso en que la venta no existe
        return HttpResponse("La venta no existe.")
    
    # Generar el nombre del archivo PDF usando el código de venta
    nombre_archivo = f"venta_{venta.venCodigo}.pdf"

    # Configurar la respuesta del PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{nombre_archivo}"'

    # Crear el documento PDF
    doc = SimpleDocTemplate(response, pagesize=portrait (letter), title="Factura de la Venta.PDF")

    # Crear una lista para almacenar los elementos del PDF
    elementos = []
    
    imagen_path = 'media/iconoBlanco.png'  # Reemplaza con la ruta de tu imagen
    imagen = Image(imagen_path, width=400, height=100)  # Ajusta el ancho y alto según tu preferencia
    elementos.append(imagen)
    
    # Establecer el estilo del documento
    estilos = getSampleStyleSheet()
    titulo_estilo = estilos['Heading2']
    titulo_estilo.alignment = 1  # Centrar el título
    
    # Agregar el título del PDF
    elementos.append(Paragraph("FACTURA DE VENTA", titulo_estilo))
    elementos.append(Spacer(1, 10))
    
    # Agregar detalles completos de la venta al PDF
    elementos.append(Paragraph(f"<strong>Código Factura:</strong> {venta.venCodigo}", estilos['Heading3']))
    elementos.append(Paragraph(f"<strong>Vendedor:</strong> {venta.venVendedor.username}", estilos['Normal']))
    elementos.append(Paragraph(f"<strong>Cliente:</strong> {venta.venCliente}", estilos['Normal']))
    elementos.append(Paragraph(f"<strong>Fecha Entrega:</strong> {venta.fechaHoraCreacion}", estilos['Normal']))
    elementos.append(Paragraph(f"<strong>Observaciones:</strong> {venta.venObservaciones}", estilos['Normal']))
    elementos.append(Spacer(1, 10))

    elementos.append(Spacer(1, 20))
    elementos.append(Paragraph("<u>Detalles de la Venta</u>", estilos['Normal']))
    elementos.append(Spacer(1, 20))
    
    # Agregar detalles de la venta en una tabla
    detalles = [[Paragraph('<strong>Código</strong>', estilos['Normal']), 
                 Paragraph('<strong>Producto</strong>', estilos['Normal']),
                 Paragraph('<strong>Cantidad</strong>', estilos['Normal']),
                 Paragraph('<strong>Precio</strong>', estilos['Normal']),
                 Paragraph('<strong>Precio Acumulado</strong>', estilos['Normal'])]]

    for detalle in venta.detalleventa_set.all():
        detalles.append([
            Paragraph(detalle.detProducto.proCodigo, estilos['Normal']),
            Paragraph(detalle.detProducto.proNombre, estilos['Normal']),
            Paragraph(str(detalle.detCantidad), estilos['Normal']),
            Paragraph(f"${detalle.detPrecioUnitario}", estilos['Normal']),
            Paragraph(f"${detalle.detPrecioAcumulativo}", estilos['Normal']),
        ])

    # Crear la tabla y aplicar el estilo
    colorT = colors.Color(0.9019607843137255, 0.9254901960784314, 0.9607843137254902)
    tabla = Table(detalles, colWidths=[1.2 * inch, 3.2 * inch, 0.8 * inch, 1.2 * inch, 1.5 * inch])
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colorT),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 1), (-1, -1), 1, colors.black)
    ]))

    # Agregar los elementos al PDF
    elementos.append(tabla)

   # Crear un estilo para centrar el texto
    centrado_estilo = ParagraphStyle(name='centrado', alignment=1)

    texto_final = Paragraph("Gracias por su compra, esperamos que vuelva pronto.", centrado_estilo)
    elementos.append(Spacer(1, 80))
    elementos.append(texto_final)

    # Centrar los últimos textos
    elementos.append(Paragraph("Administración - Unielectricos", centrado_estilo))
    elementos.append(Paragraph("Calle 5 #4-08 - 8720547", centrado_estilo))

    # Construir el documento PDF
    doc.build(elementos)

    return response



@login_required(login_url='/')
def listaDevoluciones(request):
    devoluciones = DevolucionVenta.objects.all().order_by('-fechaHoraActualizacion')
    productos = Producto.objects.all()
    retorno = {'devoluciones': devoluciones, 'productos': productos}
    if request.user.groups.filter(name='Administrador').exists():
        return render(request, 'Administrador/listarDevoluciones.html', retorno)
    else:
        return render(request, 'Empleado/listarVentas.html', retorno)   
    


@login_required(login_url='/')
def vistaRegistrarDevCliente(request, codigoVenta):
    venta = get_object_or_404(Venta, venCodigo=codigoVenta)
    usuario = request.user
    productos = Producto.objects.filter(detalleventa__detVenta=venta)
    
    retorno = {'usuario': usuario, 'productos': productos, 'venta': venta, 'codigoVenta': venta.venCodigo}

    if request.user.groups.filter(name='Administrador').exists():
        return render(request,"Administrador/frmRegistrarDevCliente.html", retorno)
    else:
        return render(request, 'Empleado/frmRegistrarDevCliente.html', retorno)



@login_required(login_url='/')
def registrarDevolucionesCli(request):
    if request.method == "POST":
        codigoVenta = request.POST.get('codigoVenta')
        venta = get_object_or_404(Venta, venCodigo=codigoVenta)
        
        usuario = int(request.POST.get('usuario'))
        
        if not usuario:
            return JsonResponse({'estado': False, 'mensaje': 'Falta el campo "usuario" en los datos POST.'})
        
        devUsuarioRecibe = User.objects.get(pk=usuario)
        
        productosDevueltos = json.loads(request.POST.get('productosDevueltos'))
        if not productosDevueltos:
            return JsonResponse({'estado': False, 'mensaje': 'No se registraron productos en la Devolución.'})
        
        precioTotal = sum(float(producto['precioAcumulado']) if producto['precioAcumulado'] else 0 for producto in productosDevueltos)

        with transaction.atomic():
            # Crea una instancia de Devolucion
            devolucion = DevolucionVenta.objects.create(
                devVenta=venta,
                devUsuarioRecibe=devUsuarioRecibe,
                devCliente=venta.venCliente,
                devDireccion=venta.venDireccion,
                devPrecioTotal=precioTotal,
            )

            for productoDevuelto in productosDevueltos:
                idProducto = int(productoDevuelto['codigo'])
                cantidadDevuelta = int(productoDevuelto['cantidad'])
                precio = float(productoDevuelto['precio'])
                precioAcumulado = float(productoDevuelto['precioAcumulado'])
                MetodoDevolucion = productoDevuelto['MetodoDevolucion']
                producto = Producto.objects.get(pk=idProducto)
                
                # Crea una instancia de DetalleDevolucionVenta
                detalleDevolucionObj = DetalleDevolucionVenta(
                    devDevolucion=devolucion,
                    devMetodo=MetodoDevolucion,
                    devProducto=producto,
                    devCantidad=cantidadDevuelta,
                    devPrecioUnitario=precio,
                    devPrecioAcumulativo=precioAcumulado,
                )
                
                detalleDevolucionObj.save()
                
                # Realiza la resta en DetalleVenta solo si el método no es "Cambiar por un producto igual"
                if MetodoDevolucion == "Devolver dinero":                
                    detalle_venta = DetalleVenta.objects.get(detVenta=venta, detProducto=producto)
                    detalle_venta.detCantidad -= cantidadDevuelta
                    detalle_venta.detDevueltos += cantidadDevuelta
                    precioUnitario = detalle_venta.detPrecioUnitario
                    detalle_venta.detPrecioAcumulativo -= precioUnitario * cantidadDevuelta
                    detalle_venta.save()

                    producto.proCantidad += cantidadDevuelta
                        
                else:
                    detalle_venta = DetalleVenta.objects.get(detVenta=venta, detProducto=producto)
                    detalle_venta.detDevueltos += cantidadDevuelta
                    detalle_venta.save()

                producto.save()
                
            # Restablece la cantidad vendida total en la venta si no se eligió "Cambiar por un producto igual"
            if all(producto['MetodoDevolucion'] == "Devolver dinero" for producto in productosDevueltos):
                venta.venPrecioTotal -= precioTotal
                venta.save()
            
            codigoDevolucion = devolucion.pk
            
        return JsonResponse({'estado': True, 'mensaje': f'Devolucion registrada exitosamente con el codigo {codigoDevolucion}.'})
      
    return render(request, 'Administrador/frmRegistrarDevCliente.html')




@login_required(login_url='/')
def listaUnidad(request):
    try:
        unidad = UnidadMedida.objects.all().order_by('-fechaHoraActualizacion')
        mensaje=""
        retorno = {"mensaje": mensaje, "listaUnidad": unidad}
        if request.user.groups.filter(name='Administrador').exists():
            return render(request, "Administrador/listarUnidadMedida.html",retorno)
        else:
            return render(request, "Empleado/listarUnidadMedida.html",retorno)
    except Error as error:
        mensaje = f"problemas al listar Unidad {error}"
    retorno = {"mensaje": mensaje, "listaUnidad": unidad}
    return render (request, "Administrador/listarUnidadMedida.html",retorno)



@login_required(login_url='/')
def vistaRegistrarUnidad(request):
    if request.user.groups.filter(name='Administrador').exists():
        return render(request, "Administrador/frmRegistrarUnidadMedida.html")
    else:
        return render(request, "Empleado/frmRegistrarUnidadMedida.html")



@login_required(login_url='/')
def registrarUnidad(request):
    try:
        nombre = request.POST["txtNombre"]

        if not nombre:
            return JsonResponse({'estado': False, 'mensaje': 'Campos requeridos incompletos.'})
        

        with transaction.atomic():
            unidad = UnidadMedida(
                uniNombre=nombre,
            )
            unidad.save()
            
            mensaje = "Unidad Agregada Correctamente"
            estado = True
            retorno = {"mensaje": mensaje}
            
            return JsonResponse({'estado': True, 'mensaje': mensaje})

    except Exception as error:
        transaction.rollback()
        mensaje = str(error)
        return JsonResponse({'estado': False, 'mensaje': mensaje})



@login_required(login_url='/')
def eliminarUnidad(request, uniNombre):
    estado= False
    mensaje = ""
    try:
        
        unidad = UnidadMedida.objects.get(uniNombre=uniNombre)
        unidad.delete()
        mensaje = "Unidad de Medida eliminado correctamente"
        estado = True
        
    except UnidadMedida.DoesNotExist:
        mensaje = f"La unidad de Medida no existe."
       
    except Exception as e:
         mensaje = "La Unidad de Medida no se puede eliminar"
    response_data = {"estado": estado, "mensaje": mensaje}
    return JsonResponse(response_data)



@login_required(login_url='/')
def listaMarca(request):
    try:
        marca = Marca.objects.all().order_by('-fechaHoraActualizacion')
        mensaje=""
        retorno = {"mensaje": mensaje, "listaMarca": marca}
        if request.user.groups.filter(name='Administrador').exists():
            return render(request, "Administrador/listarMarcas.html",retorno)
        else:
            return render(request, "Empleado/listarMarcas.html",retorno)
    except Error as error:
        mensaje = f"problemas al listar Marca {error}"
    return render (request, "Administrador/listarMarcas.html",retorno)



@login_required(login_url='/')
def vistaRegistrarMarca(request):
    if request.user.groups.filter(name='Administrador').exists():
        return render(request, "Administrador/frmRegistrarMarca.html")
    else:
        return render(request, "Empleado/frmRegistrarMarca.html")



@login_required(login_url='/')
def registrarMarca(request):
    try:
        nombre = request.POST["txtNombre"]

        if not nombre:
            return JsonResponse({'estado': False, 'mensaje': 'Campos requeridos incompletos.'})


        with transaction.atomic():
            marca = Marca(
                marcaNombre=nombre,
            )
            marca.save()
            mensaje = "Marca Agregada Correctamente"
            estado= True
            retorno = {"mensaje": mensaje}
            return JsonResponse({'estado': True, 'mensaje': mensaje})


    except Exception as error:
        transaction.rollback()
        mensaje = str(error)
        return JsonResponse({'estado': False, 'mensaje': mensaje})


    retorno = {"mensaje": mensaje}
    return render(request, "Administrador/frmRegistrarMarca.html", retorno)



@login_required(login_url='/')
def eliminarMarca(request, marcaNombre):
    try:
        marca = Marca.objects.get(marcaNombre=marcaNombre)
        marca.delete()
        mensaje = "Marca eliminada correctamente"
        return JsonResponse({'estado': True, 'mensaje': mensaje})
    except Marca.DoesNotExist:
        mensaje = "La Marca no existe"
        return JsonResponse({'estado': False, 'mensaje': mensaje})
    except Exception as e:
        mensaje = "La Marca no se puede eliminar"
        return JsonResponse({'estado': False, 'mensaje': mensaje})



def salir(request):
    auth.logout(request)
    return render(request, "frmInicioSesion.html")

#----------------Error 404-------------------------------------------------

def error404(request, exception):
    return render(request, 'error.html', status=404)

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------



def graficaEstadistica(request):
    plt.subplots(figsize=(14, 12))
    # Obtener el total de ventas
    totalVentas = DetalleVenta.objects.aggregate(TotalVentas=Sum('detPrecioAcumulativo'))['TotalVentas']
    
    # Obtener las ventas por producto
    ventasProducto = DetalleVenta.objects.values('detProducto__proNombre').annotate(cantidadProducto=Sum('detCantidad'))
  
    color = '#F1BCBC'
    color2 = '#ABEBC6'
    color3 = '#fdc275'
    listaDatos = []
    info = []
   
    
    for ventaProducto in ventasProducto:
        producto = ventaProducto['detProducto__proNombre']
        precioTotalVentas = ventaProducto['cantidadProducto']
        # porcentajeVenta = (precioTotalVentas / totalVentas) * 100
        info.append(producto)
        listaDatos.append(precioTotalVentas)
    
     
    plt.subplot(3, 3, 1)  
    plt.title("Productos más vendidos")    
    plt.xlabel("Productos") 
    plt.ylabel("Ventas", labelpad=15)
    plt.xticks(rotation=45, ha="right")
    
    # print(info)
    plt.bar(info, listaDatos, color=color)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
#---------------------------------------------------------------------------------------   
    dias = ["Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]

    # Consulta para obtener las ventas totales por día de la semana
    consultaVentasDiasSemana = ( DetalleVenta.objects.annotate(dia_semana=ExpressionWrapper(
            Func(F('detVenta__fechaHoraCreacion'), function='DAYOFWEEK'), 
            output_field=IntegerField()
        ))
        .values('dia_semana').annotate(TotalVentasDiaSemana=Sum('detCantidad')).order_by('dia_semana')
    )

    # Plot
    xDias = []
    yVentaDia = []

    for ventaDiaSemana in consultaVentasDiasSemana:
        yVentaDia.append(ventaDiaSemana['TotalVentasDiaSemana'])
        dia = ventaDiaSemana['dia_semana']
        xDias.append(dias[dia - 1])


    plt.subplot(3, 3, 2) 
    plt.title("Ventas por dia de semana")
    plt.xlabel("Día de la Semana")
    plt.ylabel("Ventas")
    plt.xticks(rotation=45, ha="right")
    
    plt.bar(xDias, yVentaDia, color=color2)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    
#----------------------------------------------------------------------------------
    Mes = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

    # Consulta para obtener las ventas totales por día de la semana
    consultaVentasMes = (
        DetalleVenta.objects.annotate(mess=ExpressionWrapper(
            Func(F('detVenta__fechaHoraCreacion'), function='MONTH'), 
            output_field=IntegerField()
        ))
        .values('mess').annotate(totalMes=Sum('detCantidad')).order_by('mess')
    )

    # Plot
    xMes = []
    yVentaMes = []

    for ventaMes in consultaVentasMes:
        print(ventaMes)
        yVentaMes.append(ventaMes['totalMes'])
        mes = ventaMes['mess']
        xMes.append(Mes[mes - 1])

    plt.subplot(3, 3, 3) 
    plt.title("Ventas por mes")
    plt.xlabel("Mes")
    plt.ylabel("Ventas")
    plt.xticks(rotation=45, ha="right")
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    plt.bar(xMes, yVentaMes, color=color3)
    
 #-------------------------------------------------------------------------------------------------------------------------------------
    productos_stock = Producto.objects.values('proNombre').annotate(cantidadStock=F('proCantidad')).order_by('-cantidadStock')[:5]

    nombres_productos = [producto['proNombre'] for producto in productos_stock]
    cantidades_stock = [producto['cantidadStock'] for producto in productos_stock]

    plt.subplot(3, 3, 4)  # Puedes ajustar el número de la subgráfica según tu diseño
    plt.title("Productos con mayor cantidad en stock")
    plt.xlabel("Productos")
    plt.ylabel("Cantidad en Stock", labelpad=15)
    plt.xticks(rotation=45, ha="right")

    plt.bar(nombres_productos, cantidades_stock, color='#e9b6f5')
    plt.tight_layout(pad=3.0)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    

#------------------------------------------------------------------------------------------------------------------------------

    productos_mes_mas_vendidos = (
    DetalleVenta.objects
    .annotate(mes=ExpressionWrapper(
        Func(F('detVenta__fechaHoraCreacion'), function='MONTH'), 
        output_field=IntegerField()
    ))
    .values('detProducto__proNombre', 'mes')
    .annotate(totalVentasMes=Sum('detCantidad'))
    .order_by('mes', '-totalVentasMes')
)

# Crear un diccionario para almacenar datos por mes
    datos_por_mes = {}
    for venta_mes in productos_mes_mas_vendidos:
        mes = venta_mes['mes']
        producto = venta_mes['detProducto__proNombre']
        ventas_mes = venta_mes['totalVentasMes']

    if mes not in datos_por_mes:
        datos_por_mes[mes] = {'productos': [], 'ventas': []}

    datos_por_mes[mes]['productos'].append(producto)
    datos_por_mes[mes]['ventas'].append(ventas_mes)

    # Crear subgráficas para cada mes
    subgrafica_num = 7  # Ajusta el número de la subgráfica según tu diseño
    for mes, datos in datos_por_mes.items():
        plt.subplot(3, 3, 5)
        plt.title(f"Productos más vendidos - {Mes[mes - 1]}")
        plt.xlabel("Productos")
        plt.ylabel("Ventas")
        plt.xticks(rotation=45, ha="right")
        
        plt.bar(datos['productos'], datos['ventas'], color='#9fd7fc')
    
    subgrafica_num += 1

    plt.tight_layout(pad=3.0)
    plt.subplots_adjust(wspace=0.2, hspace=0.5)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
#-----------------------------------------------------------------------------------------------------------------------------

    productos_menos_vendidos = Producto.objects.values('proNombre').annotate(cantidadVentas=F('proVenta')).order_by('cantidadVentas')[:5]

    nombres_productos_menos_vendidos = [producto['proNombre'] for producto in productos_menos_vendidos]
    cantidades_menos_vendidos = [producto['cantidadVentas'] for producto in productos_menos_vendidos]

# Crear subgráfica para "PRODUCTOS MENOS VENDIDOS"
    plt.subplot(3, 3, 6)  # Ajusta el número de la subgráfica según tu diseño
    plt.title("Productos menos vendidos")
    plt.xlabel("Productos")
    plt.ylabel("Cantidad de Ventas", labelpad=15)
    plt.xticks(rotation=45, ha="right")

    plt.bar(nombres_productos_menos_vendidos, cantidades_menos_vendidos, color='#f1f753')
    plt.tight_layout(pad=3.0)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.xticks(rotation=45, ha="right")
    
    imagen3 = os.path.join(settings.MEDIA_ROOT +"\\"+"grafica3.png")
    plt.savefig(imagen3)
    plt.tight_layout()
    plt.close()
   
    return render(request, "Administrador/frmEstadisticas.html")




def vistaManualA(request):
    return render(request, 'Administrador/ManualA.html', {'MANUAl': 'media/MANUAL.pdf'})



def DescargarApp(request):
    rutaApp = 'media/app-debug.apk'
    if os.path.exists(rutaApp):
        # Crear el objeto BytesIO para almacenar el contenido del archivo
        response = BytesIO()

        # Abre el archivo en modo binario
        with open(rutaApp, 'rb') as archivo:
            # Copia el contenido del archivo al objeto BytesIO
            response.write(archivo.read())

        # Configura la respuesta para el archivo
        response.seek(0)
        return FileResponse(response, as_attachment=True, filename=os.path.basename(rutaApp))
    else:
        # Manejo si el archivo no existe
        return HttpResponse("El archivo no se encuentra disponible.", status=404)

# class LoginView(APIView):
#     def post(self, request):
#         # Recuperamos las credenciales y autenticamos al usuario
#         username = request.data.get('username', None)
#         password = request.data.get('password', None)
#         user = authenticate(username=username, password=password)

#         # Si es correcto añadimos a la request la información de sesión
#         if user:
#             # login(request, user)
#             return Response(
#                  UserSerializer(user).data,
#                 status=status.HTTP_200_OK)

#         # Si no es correcto devolvemos un error en la petición
#         return Response(
#             status=status.HTTP_404_NOT_FOUND)


# class ProductoImagen(APIView):
#     def post(self, request):
#         serializer = ProductoSerializer(data=request.data)
#         if serializer.is_valid():
#             validated_data = serializer.validated_data

#             # Genera el código automático
#             nombre = validated_data['proNombre']
#             cantidad = Producto.objects.all().count()
#             nombre_abreviado = nombre[:3]
#             codigoProducto = nombre_abreviado.upper() + str(cantidad + 1).rjust(4, '0')

#             archivo = validated_data['proFoto']
#             archivo.name = 'producto.png'
#             validated_data['proFoto'] = archivo
#             validated_data['proCodigo'] = codigoProducto  # Agrega el código al validated_data

#             producto = Producto(**validated_data)
#             producto.save()

#             # Incluye el código en la respuesta
#             serializer_response = ProductoSerializer(producto)
#             return Response(serializer_response.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class ProductoImagen(APIView):
#     def post(self, request):
#         serializer= ProductoSerializer(data=request.data)
#         if serializer.is_valid():
#             validated_data = serializer.validated_data
#             archivo = validated_data['proFoto']
#             archivo.name = 'producto.png'
#             validated_data['proFoto'] = archivo
#             producto = Producto(**validated_data)
#             producto.save()
#             serializer_response = ProductoSerializer(producto)
#             return Response(serializer_response.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductoImagen(APIView):
    def post(self, request):
        serializer = ProductoSerializerImg(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            nombre = validated_data['proNombre']
            
            # Generar el código automáticamente
            codigo_base = nombre.upper()[:3]  # Tomar las primeras 3 letras en mayúsculas
            productos_con_mismo_codigo = Producto.objects.filter(proCodigo__startswith=codigo_base)
            if productos_con_mismo_codigo.exists():
                ultimo_producto = productos_con_mismo_codigo.order_by('-proCodigo').first()
                ultimo_codigo = ultimo_producto.proCodigo[3:]  # Obtener los últimos 4 dígitos del código
                nuevo_codigo_numero = int(ultimo_codigo) + 1
                nuevo_codigo = f"{codigo_base}{nuevo_codigo_numero:04d}"
            else:
                nuevo_codigo = f"{codigo_base}0001"

            archivo = validated_data['proFoto']
            archivo.name = 'producto.png'
            validated_data['proFoto'] = archivo

            # Asignar el nuevo código al producto
            validated_data['proCodigo'] = nuevo_codigo
            
            producto = Producto(**validated_data)
            producto.save()
            serializer_response = ProductoSerializerImg(producto)
            return Response(serializer_response.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def iniciarSesionAPI(request,usuario,contraseña):
    username = usuario
    password = contraseña
    user = authenticate(username=username, password=password)
    print(user)
    if user is not None:
    #registrar la variable de sesion
        auth.login(request, user)
        if user.groups.filter(name='Administrador').exists():
            return JsonResponse({'mensaje':'Inicio de sesion exitoso como administrador','estado':True,'username':request.user.username,
                                 'correo':request.user.email,'nombre':request.user.first_name,'apellidos':request.user.last_name})
        else:
            return JsonResponse({'mensaje':'Inicio de Sesion exitoso como asesor', 'estado':True,'user':request.user})
    else:
        mensaje = "El usuario o contraseña son incorrectas"
        return JsonResponse({'mensaje':mensaje,'estado':False})
    



class ProductoList(generics.ListCreateAPIView):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

class ProductoDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    lookup_field = 'proCodigo'

class UnidadMedidaList(generics.ListCreateAPIView):
    queryset = UnidadMedida.objects.all()
    serializer_class = UnidadMedidaSerializer

class UnidadMedidaDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = UnidadMedida.objects.all()
    serializer_class = UnidadMedidaSerializer

class MarcaList(generics.ListCreateAPIView):
    queryset = Marca.objects.all()
    serializer_class = MarcaSerializer

class MarcaDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Marca.objects.all()
    serializer_class = MarcaSerializer

class UserList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class ProveedorList(generics.ListCreateAPIView):
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer

class ProveedorDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer

class CompraList(generics.ListCreateAPIView):
    queryset = Compra.objects.all()
    serializer_class = CompraSerializer

class CompraDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Compra.objects.all()
    serializer_class = CompraSerializer

class DetalleCompraList(generics.ListCreateAPIView):
    queryset = DetalleCompra.objects.all()
    serializer_class = DetalleCompraSerializer

class DetalleCompraDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = DetalleCompra.objects.all()
    serializer_class = DetalleCompraSerializer

class VentaList(generics.ListCreateAPIView):
    queryset = Venta.objects.all()
    serializer_class = VentaSerializer

class VentaDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Venta.objects.all()
    serializer_class = VentaSerializer

class DetalleVentaList(generics.ListCreateAPIView):
    queryset = DetalleVenta.objects.all()
    serializer_class = DetalleVentaSerializer

class DetalleVentaDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = DetalleVenta.objects.all()
    serializer_class = DetalleVentaSerializer