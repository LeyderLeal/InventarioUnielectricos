import json
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from appInventario.models import *


class ModeloTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.unidad_medida = UnidadMedida.objects.create(uniNombre='Unidad de medida de prueba')
        self.marca = Marca.objects.create(marcaNombre='Marca de prueba')
        self.proveedor = Proveedor.objects.create(
            proTipo='Persona Natural',
            proIdentificacion='123',
            proNombre='Leyder Arlex',
        )
        self.producto = Producto.objects.create(
            proCodigo='codigo_producto',
            proNombre='Producto de prueba',
            proDescripcion='Descripción de prueba',
            proMarca=self.marca,
            proUnidadMedida=self.unidad_medida,
            proPrecio='10.0',
            proVenta=0,
            proCompra=0,
            proCantidad=0,
            proDefectuoso=0,
        )

    def test_creacion_objetos(self):
        self.assertEqual(UnidadMedida.objects.count(), 1)
        self.assertEqual(Marca.objects.count(), 1)
        self.assertEqual(Proveedor.objects.count(), 1)
        self.assertEqual(Producto.objects.count(), 1)

    def test_modelo_unidad_medida(self):
        unidad_medida = UnidadMedida.objects.get(uniNombre='Unidad de medida de prueba')
        self.assertEqual(unidad_medida.uniNombre, 'Unidad de medida de prueba')

    def test_modelo_marca(self):
        marca = Marca.objects.get(marcaNombre='Marca de prueba')
        self.assertEqual(marca.marcaNombre, 'Marca de prueba')

    def test_modelo_proveedor(self):
        proveedor = Proveedor.objects.get(proNombre='Leyder Arlex')
        self.assertEqual(proveedor.proNombre, 'Leyder Arlex')

    def test_modelo_producto(self):
        producto = Producto.objects.get(proCodigo='codigo_producto')
        self.assertEqual(producto.proCodigo, 'codigo_producto')

    def test_modelo_compra(self):
        compra = Compra.objects.create(
            comUsuarioRecibe=self.user,
            comProveedor=self.proveedor,
            comPrecioTotal=100.0,
        )
        self.assertEqual(compra.comUsuarioRecibe, self.user)
        self.assertEqual(compra.comProveedor, self.proveedor)
        self.assertEqual(compra.comPrecioTotal, 100.0)

    def test_modelo_detalle_compra(self):
        compra = Compra.objects.create(
            comUsuarioRecibe=self.user,
            comProveedor=self.proveedor,
            comPrecioTotal=100.0,
        )
        detalle_compra = DetalleCompra.objects.create(
            detCompra=compra,
            detProducto=self.producto,
            detCantidad=5,
            detPrecioUnitario=10.0,
            detPrecioAcumulativo=50.0,
        )
        self.assertEqual(detalle_compra.detCompra, compra)
        self.assertEqual(detalle_compra.detProducto, self.producto)
        self.assertEqual(detalle_compra.detCantidad, 5)
        self.assertEqual(detalle_compra.detPrecioUnitario, 10.0)
        self.assertEqual(detalle_compra.detPrecioAcumulativo, 50.0)

    def test_proveedor_identificacion_unica(self):
        # Intenta crear otro proveedor con la misma identificación (debe fallar)
        with self.assertRaises(Exception):
            Proveedor.objects.create(
                proTipo='Persona Jurídica',
                proIdentificacion='123',
                proNombre='Otro Proveedor',
            )

# ----------------------------------------------------------------------------------------------------------------------------------------


class RegistrarVentaTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.unidad_medida = UnidadMedida.objects.create(uniNombre='Unidad de medida de prueba')
        self.marca = Marca.objects.create(marcaNombre='Marca de prueba')
        self.producto_codigo = 'codigo_producto_prueba'  # Define un código de producto válido
        self.producto = Producto.objects.create(
            proCodigo=self.producto_codigo,
            proNombre='Producto de prueba',
            proDescripcion='Descripción de prueba',
            proMarca=self.marca,
            proUnidadMedida=self.unidad_medida,
            proPrecio='10.0',
            proVenta=0,
            proCompra=0,
            proCantidad=0,
            proDefectuoso=0,
        )

    def test_venta_con_campos_obligatorios_vacios(self):
        response = self.client.post('/registrarVenta/', {'vendedor': self.user.id})
        self.assertEqual(response.status_code, 200)  # Asegura que la vista no redirige
        self.assertContains(response, 'Faltan campos requeridos.')

    def test_venta_sin_productos(self):
        data = {
            'cliente': 'Cliente de prueba',
            'vendedor': self.user.id,
            'productosVendidos': '[]',  # Lista de productos vacía
        }
        response = self.client.post('/registrarVenta/', data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No se registraron productos en la venta.')

    # Puedes agregar más pruebas para casos exitosos, por ejemplo, registrando una venta válida con productos.

    def test_venta_exitosa(self):
        # Get the ID of the product you created
        producto = Producto.objects.get(proCodigo=self.producto_codigo)
        data = {
            'cliente': 'Cliente de prueba',
            'vendedor': self.user.id,
            'productosVendidos': '[{"codigo": ' + str(producto.id) + ', "cantidad": 2, "precio": 10.0, "precioAcumulado": 20.0}]',
        }
        response = self.client.post('/registrarVenta/', data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Venta registrada exitosamente con el codigo 1.')  # Reemplaza 1 con el código de venta correcto

