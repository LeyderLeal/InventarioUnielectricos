from rest_framework import serializers
from appInventario.models import *
from drf_extra_fields.fields import Base64ImageField


class ProductoSerializerImg(serializers.ModelSerializer):
    proFoto = Base64ImageField(required=False)

    class Meta:
        model = Producto
        fields = ('__all__')


class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = ('__all__')


class UnidadMedidaSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnidadMedida
        fields = ('__all__')


class MarcaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marca
        fields = ('__all__')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('__all__')


class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = ('__all__')


class CompraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compra
        fields = ('__all__')


class DetalleCompraSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleCompra
        fields = ('__all__')


class VentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venta
        fields = ('__all__')


class DetalleVentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleVenta
        fields = ('__all__')

