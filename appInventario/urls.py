from django.urls import path
from . import views
from rest_framework.documentation import include_docs_urls



urlpatterns = [
    path('producto',views.ProductoList.as_view()),
  #  path('producto/<int:pk>',views.ProductoDetail.as_view()),
    path('producto/<str:proCodigo>',views.ProductoDetail.as_view()),
    path('unidadmedida',views.UnidadMedidaList.as_view()),
    path('unidadmedida/<int:pk>',views.UnidadMedidaDetail.as_view()),
    path('marca',views.MarcaList.as_view()),
    path('marca/<int:pk>',views.MarcaDetail.as_view()),
    path('user',views.UserList.as_view()),
    path('user/<int:pk>',views.UserDetail.as_view()),
    path('proveedor',views.ProveedorList.as_view()),
    path('proveedor/<int:pk>',views.ProveedorDetail.as_view()),
    path('compra',views.CompraList.as_view()),
    path('compra/<int:pk>',views.CompraDetail.as_view()),
    path('detallecompra',views.DetalleCompraList.as_view()),
    path('detallecompra/<int:pk>',views.DetalleCompraDetail.as_view()),
    path('venta',views.VentaList.as_view()),
    path('venta/<int:pk>',views.VentaDetail.as_view()),
    path('detalleventa',views.DetalleVentaList.as_view()),
    path('detalleventa/<int:pk>',views.DetalleVentaDetail.as_view()),
    # path('loginMovil/',views.LoginView.as_view()),
    path('Api/inicioSesion/<str:usuario>/<str:contraseña>',views.iniciarSesionAPI),
    path('productoImagen/',views.ProductoImagen.as_view()),

    path('docs/',include_docs_urls(title='Documentacion API'))
]
