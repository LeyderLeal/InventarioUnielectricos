from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone

# Create your models here.

tipoProveedor = [
    ('Persona Júridica',"Persona Júridica"),('Persona Natural','Persona Natural'),
]

class UnidadMedida(models.Model):
    uniNombre = models.CharField(max_length=45,unique=True, db_comment="Nombre de la Unidad de Médida")
    fechaHoraCreacion  = models.DateTimeField(auto_now_add=True, db_comment="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True,db_comment="Fecha y hora última actualización")
    
    def __str__(self)->str:
        return f"{self.uniNombre}"    
        

class Marca(models.Model):
    marcaNombre = models.CharField(max_length=45,unique=True, db_comment="Nombre de la Unidad de Médida")
    fechaHoraCreacion  = models.DateTimeField(auto_now_add=True, db_comment="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True,db_comment="Fecha y hora última actualización")
    
    def __str__(self)->str:
        return f"{self.marcaNombre}"


class User(AbstractUser):
    userEstado = models.CharField(max_length=45, null = True, default="Activo")
    fechaHoraCreacion  = models.DateTimeField(auto_now_add=True,db_comment="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True,db_comment="Fecha y hora última actualización")
    
    def __str__(self):
        return f"{self.username}"
    
    
class Proveedor(models.Model):
    proTipo  = models.CharField(max_length=20,choices=tipoProveedor, db_comment="Tipo de proveedor")
    proIdentificacion = models.CharField(max_length=15, unique=True, db_comment="Identificación del proveedor, puede ser cédula o Nit")
    proNombre = models.CharField(max_length=60,db_comment="Nombre del proveedor")    
    proTelefono = models.CharField(max_length=15, null=True,db_comment="Número telefono del proveedor")    
    fechaHoraCreacion  = models.DateTimeField(auto_now_add=True,db_comment="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True,db_comment="Fecha y hora última actualización")
    
    def __str__(self)->str:
        return f"{self.proNombre}"


class Producto(models.Model):
    proCodigo = models.CharField(max_length=50, unique=True,db_comment="Código único asignado al producto")
    proNombre = models.CharField(max_length=30,db_comment="Nombre del producto")
    proDescripcion = models.CharField(max_length=60,db_comment="Descripcion del producto")
    proMarca = models.ForeignKey(Marca,on_delete=models.PROTECT, default=None,
                                        db_comment="Hace referencia a la Unidad de Medida FK")
    proUnidadMedida = models.ForeignKey(UnidadMedida,on_delete=models.PROTECT, default=None,
                                        db_comment="Hace referencia a la Unidad de Medida FK")
    proPrecio = models.CharField(max_length=11,db_comment="Precio del producto")
    proFoto = models.ImageField(upload_to=f"productos/", null=True, blank=True, db_comment="Foto del producto")    
    proVenta = models.IntegerField(default=0,db_comment="Cantidad vendidas del Producto")
    proCompra = models.IntegerField(default=0,db_comment="Cantidad ingresadas del Producto")
    proCantidad = models.IntegerField(default=0,db_comment="Cantidad actual del stock del Producto")
    fechaHoraCreacion = models.DateTimeField(auto_now_add=True,db_comment="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True,db_comment="Fecha y hora última actualización")

    def __str__(self)->str:
        return f"{self.proNombre}"


class Compra(models.Model):
    comCodigo = models.AutoField(primary_key=True, unique=True, db_comment="Codigo de la Compra")
    comUsuarioRecibe = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,
                                            db_comment="Hace referencia a usuario que recibe la compra")
    comObservaciones = models.TextField(null=True,db_comment="Observaciones que se requieran hacer")
    comProveedor = models.ForeignKey(Proveedor,on_delete=models.PROTECT,
                                        db_comment="Hace referencia al proveedor que entrega los Productos")
    comPrecioTotal = models.IntegerField(db_comment="suma de todos los precios acumulativos por producto")
    fechaHoraCreacion  = models.DateTimeField(auto_now_add=True,db_comment="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True,db_comment="Fecha y hora última actualización")

    def __str__(self)->str:
        return f"{self.comCodigo}"


class DetalleCompra(models.Model):
    detCompra = models.ForeignKey(Compra, on_delete=models.PROTECT,
                        db_comment="Hace referencia a la Compra registrada")
    detProducto = models.ForeignKey(Producto, on_delete=models.PROTECT,
                        db_comment="Hace referencia al Producto que se está registrando en la Compra")
    detCantidad=models.IntegerField(db_comment="Cantidad que ingresa del Producto")
    detDevueltos = models.IntegerField(default=0,db_comment="Cantidad devueltas del Producto")
    detPrecioUnitario = models.IntegerField(db_comment="Precio del Producto que ingresa")
    detPrecioAcumulativo = models.IntegerField(db_comment="Precio de la cantidad de productos que agrega el usuario")
    fechaHoraCreacion  = models.DateTimeField(auto_now_add=True,db_comment="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True,db_comment="Fecha y hora última actualización")
    
    def __str__(self)->str:
        return f"{self.detProducto} -> {self.detCantidad}"


class DevolucionCompra(models.Model):
    devCodigo = models.AutoField(primary_key=True, unique=True, db_comment="Codigo de la Devolucion")
    devCompra = models.ForeignKey(Compra, on_delete=models.PROTECT,db_comment="Hace referencia a la venta al cual quiere hacer la devolucion")
    devUsuarioEntrega = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,
                                            db_comment="Hace referencia a usuario que entrega la devolucion")
    devProveedor = models.CharField(max_length=50,null=True, db_comment="Hace referencia al proveedor al que se le hace entrega la devolucion")
    devPrecioTotal = models.IntegerField(db_comment="suma de todos los precios acumulativos por producto")
    devFecha = models.DateTimeField(auto_now_add=True,db_comment="Fecha y hora de la devolucion")

    def __str__(self)->str:
        return f"{self.devCompra}"
    
class DetalleDevolucionCompra(models.Model):
    devDevolucion = models.ForeignKey(DevolucionCompra, on_delete=models.PROTECT,db_comment="Hace referencia a la devolucion registrada")
    devMetodo = models.CharField(max_length=60,db_comment="metodo de la devolucion")
    devProducto = models.ForeignKey(Producto, on_delete=models.PROTECT,db_comment="Hace referencia al Producto que se está registrando en la Devolucion")
    devCantidad = models.IntegerField(db_comment="Cantidad que ingresa del Producto")
    devPrecioUnitario = models.IntegerField(db_comment="Precio del Producto devuelto")
    devPrecioAcumulativo = models.IntegerField(db_comment="Precio de la cantidad de productos que agrega el usuario")
    
    def __str__(self)->str:
        return f"{self.devProducto} -> {self.devCantidad}"


class Venta(models.Model):
    venCodigo = models.AutoField(primary_key=True, unique=True, db_comment="Codigo de la Venta")
    venVendedor = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,
                                            db_comment="Hace referencia a usuario que hace la venta")
    venObservaciones = models.TextField(null=True,db_comment="Observaciones que se requieran hacer")
    venCliente = models.CharField(max_length=50,null=True, db_comment="Hace referencia al cliente que recibe los Productos")
    venDireccion = models.CharField(max_length=50,null=True, db_comment="Hace referencia a la direccion del cliente que recibe los Productos")
    venPrecioTotal = models.IntegerField(db_comment="suma de todos los precios acumulativos por producto")
    fechaHoraCreacion  = models.DateTimeField(auto_now_add=True,db_comment="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True,db_comment="Fecha y hora última actualización")

    def __str__(self)->str:
        return f"{self.venCodigo}"
    
    
class DetalleVenta(models.Model):
    detVenta = models.ForeignKey(Venta, on_delete=models.PROTECT,
                        db_comment="Hace referencia a la Venta registrada")
    detProducto = models.ForeignKey(Producto, on_delete=models.PROTECT,
                        db_comment="Hace referencia al Producto que se está registrando en la Venta")
    detCantidad=models.IntegerField(db_comment="Cantidad que ingresa del Producto")
    detDevueltos = models.IntegerField(default=0,db_comment="Cantidad devueltas del Producto")
    detPrecioUnitario = models.IntegerField(db_comment="Precio del Producto que ingresa")
    detPrecioAcumulativo = models.IntegerField(db_comment="Precio de la cantidad de productos que agrega el usuario")
    fechaHoraCreacion  = models.DateTimeField(auto_now_add=True,db_comment="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True,db_comment="Fecha y hora última actualización")
    
    def __str__(self)->str:
        return f"{self.detProducto} -> {self.detCantidad}"
    
    
    
class DevolucionVenta(models.Model):
    devCodigo = models.AutoField(primary_key=True, unique=True, db_comment="Codigo de la Devolucion")
    devVenta = models.ForeignKey(Venta, on_delete=models.PROTECT,db_comment="Hace referencia a la venta al cual quiere hacer la devolucion")
    devUsuarioRecibe = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,
                                            db_comment="Hace referencia a usuario que recibe la devolucion")
    devCliente = models.CharField(max_length=50,null=True, db_comment="Hace referencia al cliente que entrega la devolucion")
    devDireccion = models.CharField(max_length=50,null=True, db_comment="Hace referencia a la direccion del cliente")
    devPrecioTotal = models.IntegerField(db_comment="suma de todos los precios acumulativos por producto")
    devFecha = models.DateTimeField(auto_now_add=True,db_comment="Fecha y hora de la devolucion")

    def __str__(self)->str:
        return f"{self.devCodigo}"
    
class DetalleDevolucionVenta(models.Model):
    devDevolucion = models.ForeignKey(DevolucionVenta, on_delete=models.PROTECT,db_comment="Hace referencia a la devolucion registrada")
    devMetodo = models.CharField(max_length=60,db_comment="metodo de la devolucion")
    devProducto = models.ForeignKey(Producto, on_delete=models.PROTECT,db_comment="Hace referencia al Producto que se está registrando en la Devolucion")
    devCantidad = models.IntegerField(db_comment="Cantidad que ingresa del Producto")
    devPrecioUnitario = models.IntegerField(db_comment="Precio del Producto devuelto")
    devPrecioAcumulativo = models.IntegerField(db_comment="Precio de la cantidad de productos que agrega el usuario")
    
    def __str__(self)->str:
        return f"{self.devProducto} -> {self.devCantidad}"