"""
URL configuration for GestionInventario project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path, include
from appInventario import views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import re_path as url

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.inicioSesion),
  

    path('loginX/',views.loginX),
    path('inicio/<str:mensaje>',views.inicioSesion),
    path('salir/', views.salir),
    
    
    path('inicioA/', views.inicioAdministrador),
    path('inicioE/', views.inicioEmpleado),

    path('perfil/', views.vistaPerfil),

    path('listaUsuario/', views.listaUsuario),
    path('vistaRegistrarUsuario/', views.vistaRegistrarUsuario),
    path('registrarUsuario/', views.registrarUsuario),
    path('editarUsuario/<int:id>/', views.editarUsuario),
    path('actualizarUsuario/', views.actualizarUsuario),
    path('actualizarContraseña/', views.actualizarContra),
    path('vistaRecuperarContraseña/', views.vistaRecuperarContra),    
    path('RecuperarContraseña/', views.recuperarContra),
    
    path('listaProveedor/', views.listaProveedor),
    path('vistaRegistrarProveedor/', views.vistaRegistrarProveedor),
    path('registrarProveedor/', views.registrarProveedor),
    path('editarProveedor/<int:id>/', views.editarProveedor),
    path('actualizarProveedor/', views.actualizarProveedor),
    
    
    path('listaProducto/', views.listaProducto),
    path('vistaRegistrarProducto/', views.vistaRegistrarProducto),
    path('registrarProducto/', views.registrarProducto),
    path('editarProducto/<int:id>/', views.editarProducto),
    path('actualizarProducto/', views.actualizarProducto),
    

    
    path('listaCompra/', views.listaCompra),
    path('vistaRegistrarCompra/', views.vistaRegistrarCompra),
    path('registrarCompra/', views.registrarCompra, name='registrarCompra'),


    path('listaVenta/', views.listaVenta),
    path('vistaRegistrarVenta/', views.vistaRegistrarVenta),
    path('registrarVenta/', views.registrarVenta, name='registrarVenta'),



    path('listaDevoluciones/', views.listaDevoluciones),
    path('vistaRegistrarDevolucionesCliente/<int:codigoVenta>/', views.vistaRegistrarDevCliente, name='DevolucionesCli'),
    path('registrarDevolucionesCliente/', views.registrarDevolucionesCli, name='registrarDevolucionVen'),



    path('vistaRegistrarDevolucionesProveedor/<int:codigoCompra>/', views.vistaRegistrarDevProveedor, name='DevolucionesPro'),
    path('registrarDevolucionesProveedor/', views.registrarDevolucionesPro, name='registrar_devoluciones_proveedor'),
    

    
    path('listaUnidad/', views.listaUnidad),
    path('vistaRegistrarUnidad/', views.vistaRegistrarUnidad),
    path('registrarUnidad/', views.registrarUnidad),
    
    
    path('listaMarca/', views.listaMarca),
    path('vistaRegistrarMarca/', views.vistaRegistrarMarca),
    path('registrarMarca/', views.registrarMarca),
    
    
    path('suspendeUsuario/<int:user_id>/<str:mensaje>/', views.suspendeUsuario, name='suspendeUsuario'),
    path('activaUsuario/<int:user_id>/<str:mensaje>/', views.activaUsuario, name='activaUsuario'),
    path('eliminarProducto/<str:proCodigo>/', views.eliminarProducto, name='eliminarProducto'),
    path('eliminarProveedor/<int:proIdentificacion>/', views.eliminarProveedor, name='eliminarProveedor'),
    path('eliminarUnidad/<str:uniNombre>/', views.eliminarUnidad, name='eliminarUnidad'),
    path('eliminarMarca/<str:marcaNombre>/', views.eliminarMarca, name='eliminarMarca'),
    
    path('Graficas/', views.graficaEstadistica),

    path('generar_pdf_compra/<int:compra_id>/', views.generar_pdf_compra, name='generar_pdf_compra'),
    path('generar_pdf_venta/<int:venta_id>/', views.generar_pdf_venta, name='generar_pdf_venta'),
    
    # path('ManualA/', views.vistaManualA),
    # path('DescargarManual/', views.DescargarManual),
    path('DescargarApp/', views.DescargarApp),

    
    path('', include('appInventario.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root = settings.MEDIA_ROOT)
    
    

    