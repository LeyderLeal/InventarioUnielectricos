from django.contrib import admin
from appInventario.models import *

# Register your models here.
admin.site.register(User)
admin.site.register(Proveedor)
admin.site.register(UnidadMedida)
admin.site.register(Marca)
admin.site.register(Producto)
admin.site.register(Compra)
admin.site.register(DetalleCompra)
admin.site.register(Venta)
admin.site.register(DetalleVenta)
admin.site.register(DevolucionVenta)
admin.site.register(DetalleDevolucionVenta)
admin.site.register(DevolucionCompra)
admin.site.register(DetalleDevolucionCompra)
