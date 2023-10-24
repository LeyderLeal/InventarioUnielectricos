let productos=[]

$(document).ready(function () {
  // Mostrar el precio acumulado al cambiar la cantidad o el precio unitario
  $('.calcular-precio').on('change', function () {
    calcularPrecioAcumulado();
  });
  
  // Función para calcular y mostrar el precio acumulado
  function calcularPrecioAcumulado() {
    var cantidad = parseFloat($('#frmEntradaProducto #cantidad').val()) || 0;
    var precio = parseFloat($('#frmEntradaProducto #precio').val()) || 0;
    var precioAcumulado = cantidad * precio;

    $('#frmEntradaProducto #precioAcumulado').text('$' + precioAcumulado.toFixed(2));
  }


  // Recalcular el precio total al modificar algún precio acumulativo
  function recalcularPrecioTotal() {
    var precioTotal = 0;
    $('#datosTablaProductos tr').each(function () {
      var precioAcumulado = parseFloat($(this).find('td:eq(5)').text());
      precioTotal += precioAcumulado;
    });

    $('#precioTotal').text('$' + precioTotal.toFixed(2));
  }

  // Mostrar la modal de agregar producto
  $('#btnAbrirModalAnexarProducto').click(function () {
    $('#modalProducto').modal('show');
  });
  

  $('#btnAgregarProductoDetalleCompra').click(function () {
    var codigo = $('#txtProducto').val();
    var producto = $('#txtProducto option:selected').text();
    var cantidad = $('#cantidad').val();
    var unidadMedida = $('#txtUnidadMedida').val();
    var precio = $('#precio').val();
    var precioAcumulado = precio * cantidad;

    // Obtener el precio de venta por unidad
    var precioVenta = parseFloat($('#intPrecio').val()) || 0;

    // Validar que el precio de compra no sea mayor al precio de venta
    if (precio <= precioVenta) {
        // Validar que se hayan ingresado todos los campos
        if (codigo && cantidad && precio) {
            // Crear la nueva fila de la tabla con los datos ingresados
            var fila = '<tr><td>' + codigo + '</td><td>' + producto + '</td><td>' + cantidad + '</td><td>' + unidadMedida + '</td><td>' + precio + '</td><td>' + precioAcumulado.toFixed(2) + '</td><td><button class="btn btn-danger eliminar-producto">Eliminar</button></td></tr>';

            // Agregar la fila a la tabla
            $('#datosTablaProductos').append(fila);

            // Limpiar los campos del formulario de la modal
            $('#frmEntradaProducto')[0].reset();

            // Cerrar el modal
            $('#modalProducto').modal('hide');

            // Recalcular el precio total al agregar un nuevo producto
            recalcularPrecioTotal();
        } else {
            // Mostrar mensaje de error si faltan campos por completar
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Por favor, complete todos los campos.',
            });
        }
    } else {
        // Mostrar mensaje de error si el precio de compra es mayor al precio de venta
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'El precio de compra no puede ser mayor al precio de venta.',
        });
    }
  });

  $('#datosTablaProductos').on('click', '.eliminar-producto', function () {
    // Elimina la fila completa al hacer clic en el botón de eliminar
    $(this).closest('tr').remove();
  
    // Recalcula el precio total después de eliminar un producto
    recalcularPrecioTotal();
  });

  // Evento change para actualizar el precio total al modificar algún precio acumulativo
  $('#datosTablaProductos').on('change', '.calcular-precio', function () {
    recalcularPrecioTotal();
  });

  // Obtener los datos de los productos agregados a la tabla y enviar el formulario
  $('#btnRegistrarDetalleCompra').click(function () {
    // Obtener los datos de los productos agregados a la tabla
    var productosComprados = $('#datosTablaProductos tr').map(function () {
      return {
        codigo: $(this).find('td:eq(0)').text(),
        nombre: $(this).find('td:eq(1)').text(),
        cantidad: $(this).find('td:eq(2)').text(),
        precio: $(this).find('td:eq(4)').text(),
        precioAcumulado: parseFloat($(this).find('td:eq(5)').text()),
      };
    }).get();

    // Agregar los datos al campo oculto
    $('#productosComprados').val(JSON.stringify(productosComprados));

    // Enviar el formulario
    $('#registrarCompra').submit();
  });

  $('#registrarCompra').on('submit', function (e) {
    e.preventDefault(); // Evitar el envío del formulario por defecto

    // Enviar el formulario utilizando AJAX
    $.ajax({
      type: 'POST',
      url: '/registrarCompra/',
      data: $(this).serialize(),
      dataType: 'json',
      success: function (data) {
        if (data.estado) {
          // If the purchase was successful
          Swal.fire({
            icon: 'success',
            title: 'Compra registrada',
            text: data.mensaje,
          }).then(function () {
            window.location.href = '/registrarCompra/';
          });
        } else {
          // If there was an error during the purchase
          Swal.fire({
            icon: 'error',
            title: 'Error',
            text: data.mensaje,
          });
        }
      },
      error: function (xhr, textStatus, errorThrown) {
        // If there was an error in the AJAX call
        Swal.fire({
          icon: 'error',
          title: 'Error de conexión',
          text: 'Hubo un problema. Por favor, inténtelo nuevamente',
        });
      },
    });
  });





  $('#btnAgregarProductoDetalleVenta').click(function () {
    var codigo = $('#txtProducto').val();
    var producto = $('#txtProducto option:selected').text();
    var cantidad = $('#cantidad').val();
    var unidadMedida = $('#txtUnidadMedida').val();
    var precio = $('#precio').val();
    var precioAcumulado = precio * cantidad;

      // Validar que se hayan ingresado todos los campos
      if (codigo && cantidad && precio) {
          // Crear la nueva fila de la tabla con los datos ingresados
          var fila = '<tr><td>' + codigo + '</td><td>' + producto + '</td><td>' + cantidad + '</td><td>' + unidadMedida + '</td><td>' + precio + '</td><td>' + precioAcumulado.toFixed(2) + '</td><td><button class="btn btn-danger eliminar-producto">Eliminar</button></td></tr>';

          // Agregar la fila a la tabla
          $('#datosTablaProductos').append(fila);

          // Limpiar los campos del formulario de la modal
          $('#frmEntradaProducto')[0].reset();

          // Cerrar el modal
          $('#modalProducto').modal('hide');

          // Recalcular el precio total al agregar un nuevo producto
          recalcularPrecioTotal();
      } else {
          // Mostrar mensaje de error si faltan campos por completar
          Swal.fire({
              icon: 'error',
              title: 'Error',
              text: 'Por favor, complete todos los campos.',
          });
      }
  });

  // Obtener los datos de los productos agregados a la tabla y enviar el formulario
  $("#btnRegistrarDetalleVenta").click(function () {
    // Obtener los datos de los productos agregados a la tabla
    var productosVendidos = [];

    $("#datosTablaProductos tr").each(function () {
      var codigo = $(this).find("td:eq(0)").text();
      var producto = $(this).find("td:eq(1)").text();
      var cantidad = $(this).find("td:eq(2)").text();
      var precio = $(this).find("td:eq(4)").text();
      var precioAcumulado = $(this).find("td:eq(5)").text();
      productosVendidos.push({
        codigo: codigo,
        nombre: producto,
        cantidad: cantidad,
        precio: precio,
        precioAcumulado: precioAcumulado,
      });
    });

    // Agregar los datos al campo oculto
    $("#productosVendidos").val(JSON.stringify(productosVendidos));

    // Verificar si la cantidad vendida es mayor a la cantidad disponible en el inventario
    var valid = true;
    productosVendidos.forEach(function (producto) {
      var cantidadVendida = parseInt(producto.cantidad);
      var cantidadDisponible = parseInt($("#cantidad-" + producto.codigo).val());

      if (cantidadVendida > cantidadDisponible) {
        valid = false;
        return false; // Salir del bucle si se encontró un producto con cantidad insuficiente
      }
    });

    // Si alguna cantidad vendida es mayor a la cantidad disponible, mostrar el SweetAlert
    if (!valid) {
      Swal.fire({
        icon: "error",
        title: "Cantidad insuficiente",
        text: "La cantidad vendida es mayor a la cantidad disponible en el inventario.",
      });
      return; // Detener el proceso de registro de venta
    }

    // Enviar el formulario
    $.ajax({
      type: 'POST',
      url: '/registrarVenta/', // URL of the view that processes the sale registration
      data: $("#registrarVenta").serialize(),
      dataType: 'json', // Expecting a JSON response from the server
      success: function (data) {
        if (data.estado) {
          // If the sale was successful
          Swal.fire({
            icon: 'success',
            title: 'Venta registrada',
            text: data.mensaje,
          }).then(function () {
            window.location.href = '/registrarVenta/';
          });
        } else {
          // If there was an error during the sale registration
          Swal.fire({
            icon: 'error',
            title: 'Error',
            text: data.mensaje,
          });
        }
      },
      error: function (xhr, textStatus, errorThrown) {
        // If there was an error in the AJAX call
        Swal.fire({
          icon: 'error',
          title: 'Error de conexión',
          text: 'Hubo un problema. Por favor, inténtelo nuevamente',
        });
      },
    });
  });



  $('#btnAgregarProductoDetalleDevolucion').click(function () {
    var codigo = $('#txtProducto').val();
    var producto = $('#txtProducto option:selected').text();
    var cantidad = $('#cantidad').val();
    var unidadMedida = $('#txtUnidadMedida').val();
    var precio = $('#precio').val();
    var precioAcumulado = precio * cantidad;
    var MetodoDevolucion = $('#MetodoDevolucion').val();

      // Validar que se hayan ingresado todos los campos
      if (codigo && cantidad && precio) {
          // Crear la nueva fila de la tabla con los datos ingresados
          var fila = '<tr><td>' + codigo + '</td><td>' + producto + '</td><td>' + cantidad + '</td><td>' + unidadMedida + '</td><td>' + precio + '</td><td>' + precioAcumulado.toFixed(2) + '</td><td>' + MetodoDevolucion + '</td><td><button class="btn btn-danger eliminar-producto">Eliminar</button></td></tr>';
  
          // Agregar la fila a la tabla
          $('#datosTablaProductos').append(fila);
  
          // Limpiar los campos del formulario de la modal
          $('#frmEntradaProducto')[0].reset();
  
          // Cerrar el modal
          $('#modalProducto').modal('hide');
  
          // Recalcular el precio total al agregar un nuevo producto
          recalcularPrecioTotal();
      } else {
          // Mostrar mensaje de error si faltan campos por completar
          Swal.fire({
              icon: 'error',
              title: 'Error',
              text: 'Por favor, complete todos los campos.',
          });
      }
  });



  // Obtener los datos de los productos agregados a la tabla y enviar el formulario
  $("#btnRegistrarDetalleDevolucionCompra").click(function () {
    // Obtener los datos de los productos agregados a la tabla
    var productosDevueltos = [];

    $("#datosTablaProductos tr").each(function () {
      var codigo = $(this).find("td:eq(0)").text();
      var producto = $(this).find("td:eq(1)").text();
      var cantidad = $(this).find("td:eq(2)").text();
      var precio = parseFloat($(this).find("td:eq(4)").text());
      var precioAcumulado = parseFloat($(this).find("td:eq(5)").text());
      var MetodoDevolucion = $(this).find("td:eq(6)").text();
      productosDevueltos.push({
        codigo: codigo,
        nombre: producto,
        cantidad: cantidad,
        precio: precio,
        precioAcumulado: precioAcumulado,
        MetodoDevolucion: MetodoDevolucion,
      });
      console.log("Código: " + codigo + ", Producto: " + producto + ", Cantidad: " + cantidad);
    });

    // Agregar los datos al campo oculto
    $("#productosDevueltos").val(JSON.stringify(productosDevueltos));
    
    $('#frmEntradaProducto').submit();
  
    // Enviar el formulario
    $.ajax({
      type: 'POST',
      url: '/registrarDevolucionesProveedor/', 
      data: $("#registrarDevolucionesProveedor").serialize(),
      dataType: 'json',
      success: function (data) {
        if (data.estado) {
          // If the sale was successful
          Swal.fire({
            icon: 'success',
            title: 'Devolucion registrada',
            text: data.mensaje,
          }).then(function () {
            window.location.href = '/registrarDevolucionesProveedor/';
          });
        } else {
          // If there was an error during the sale registration
          Swal.fire({
            icon: 'error',
            title: 'Error',
            text: data.mensaje,
          });
        }
      },
      error: function (xhr, textStatus, errorThrown) {
        // If there was an error in the AJAX call
        Swal.fire({
          icon: 'error',
          title: 'Error de conexión',
          text: 'Hubo un problema. Por favor, inténtelo nuevamente',
        });
      },
    });
  });



  // Obtener los datos de los productos agregados a la tabla y enviar el formulario
  $("#btnRegistrarDetalleDevolucionVenta").click(function () {
    // Obtener los datos de los productos agregados a la tabla
    var productosDevueltos = [];

    $("#datosTablaProductos tr").each(function () {
      var codigo = $(this).find("td:eq(0)").text();
      var producto = $(this).find("td:eq(1)").text();
      var cantidad = $(this).find("td:eq(2)").text();
      var precio = parseFloat($(this).find("td:eq(4)").text());
      var precioAcumulado = parseFloat($(this).find("td:eq(5)").text());
      var MetodoDevolucion = $(this).find("td:eq(6)").text();
      productosDevueltos.push({
        codigo: codigo,
        nombre: producto,
        cantidad: cantidad,
        precio: precio,
        precioAcumulado: precioAcumulado,
        MetodoDevolucion: MetodoDevolucion,
      });
    });

    // Agregar los datos al campo oculto
    $("#productosDevueltos").val(JSON.stringify(productosDevueltos));

    
    $('#frmEntradaProducto').submit();
    
  
    // Enviar el formulario
    $.ajax({
      type: 'POST',
      url: '/registrarDevolucionesCliente/', // URL of the view that processes the sale registration
      data: $("#registrarDevolucionesCliente").serialize(),
      dataType: 'json', // Expecting a JSON response from the server
      success: function (data) {
        if (data.estado) {
          // If the sale was successful
          Swal.fire({
            icon: 'success',
            title: 'Devolucion registrada',
            text: data.mensaje,
          }).then(function () {
            window.location.href = '/registrarDevolucionesCliente/';
          });
        } else {
          // If there was an error during the sale registration
          Swal.fire({
            icon: 'error',
            title: 'Error',
            text: data.mensaje,
          });
        }
      },
      error: function (xhr, textStatus, errorThrown) {
        // If there was an error in the AJAX call
        Swal.fire({
          icon: 'error',
          title: 'Error de conexión',
          text: 'Hubo un problema. Por favor, inténtelo nuevamente',
        });
      },
    });
  });

});


// Definir una variable global para almacenar la cantidad vendida
let cantidadVendida;
let cantidadComprada;
// Definir la función validarCantidad fuera del evento DOMContentLoaded<
function validarCantidad() {
  var cantidadInput = $('#cantidad');
  var cantidadIngresada = parseFloat(cantidadInput.val());
  
  if (isNaN(cantidadIngresada) || cantidadIngresada <= 0 || cantidadIngresada > cantidadVendida) {
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: 'La cantidad ingresada no es válida. Debe ser un valor mayor a 0 y menor o igual a la cantidad vendida del producto.',
    });
    cantidadInput.val('');
  }

  if (isNaN(cantidadIngresada) || cantidadIngresada <= 0 || cantidadIngresada > cantidadComprada) {
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: 'La cantidad ingresada no es válida. Debe ser un valor mayor a 0 y menor o igual a la cantidad comprada del producto.',
    });
    cantidadInput.val('');
  }
}

document.addEventListener("DOMContentLoaded", function () {
  // Agregar el evento onchange al elemento txtProducto (menú desplegable)
  $('#txtProducto').on('change', function () {
    // Obtener el valor del data-producto-id de la opción seleccionada
    var selectedProductoId = $(this).find('option:selected').data('producto-id');

    // Verificar si se seleccionó una opción válida
    if (selectedProductoId) {
      // Obtener la cantidad vendida del producto seleccionado en la tabla
      cantidadVendida = parseFloat($("tbody tr[data-cantidad-vendida][data-producto-id='" + selectedProductoId + "']").attr("data-cantidad-vendida"));
      cantidadComprada = parseFloat($("tbody tr[data-cantidad-comprada][data-producto-id='" + selectedProductoId + "']").attr("data-cantidad-comprada"));
    }
  });

  // Agregar el evento onchange al elemento cantidad
  $('#cantidad').on('change', validarCantidad);
});


function cargarProductos(id,codigo,nombre,descripcion,cantidad,precio,unidadMedida,imagen,marca){
  let producto = {
    "id":id,
    "codigo":codigo,
    "nombre":nombre,
    "descripcion":descripcion,
    "cantidad":cantidad,
    // "ventas":ventas,
    // "compras":compras,
    "precio":precio,
    "marca":marca,
    "unidadMedida":unidadMedida,
    "imagen":imagen,
    
  }
  productos.push(producto)
}



//muestra modal con el detalle del producto seleccionado
function detalleProductos(codigo){  
  let datos=""
  productos.forEach(entrada =>{
    pos = productos.findIndex(producto=>producto.codigo == codigo)
    datos = `<div class= "mb-4 text-center">
    <label for="fileFoto" class="fw-bold">Foto Producto</label>
    <div class="text-center">
        <img src="../media/${productos[pos].imagen}" width="110" height="110" alt="">
    </div>
    <br>
    
    <div class="form-group row">
    <div class="col-lg-4 mb-3">
        <h6 class="fw-bold">Código:</h6>
        <p id="" class="text-dark">${productos[pos].codigo}</p>
    </div>
    
    <div class="col-lg-4 mb-3">
        <h6 class="fw-bold">Nombre:</h6>
        <p id="txtNombre" class="">${productos[pos].nombre}</p>
    </div>
    
    <div class="col-lg-4 mb-3">
        <h6 class="fw-bold">Precio:</h6>
        <p id="" class="precio">$${formatNumberWithCommas(productos[pos].precio)}</p>
    </div>
    </div>
    
    <div class="form-group row">
    <div class="col-lg-4 mb-3">
        <h6 class="fw-bold">Stock:</h6>
        <p id="txtCantidad" class="">${productos[pos].cantidad}</p>
    </div>


    <div class="col-lg-4 mb-3">
        <h6 class="fw-bold">Marca:</h6>
        <p id="txtMarca">${productos[pos].marca}</p>
    </div>
    
    <div class="col-lg-4 mb-3">
        <h6 class="fw-bold">Unidad Medida:</h6>
        <p id="txtUnidadMedida" class="">${productos[pos].unidadMedida}</p>
    </div>
    </div>

    <div class="mb-3 text-center">
        <h6 class="fw-bold">Descripcion:</h6>
        <div class="text-center">
        <p id="txtDescripcion" class="text-center">${productos[pos].descripcion}</p>
    </div>
    </div>
    `
    document.getElementById("datosModal").innerHTML = datos

  })
}

function formatNumberWithCommas(number) {
  return number.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
}



//funcion de mostrar los productos con poca cantidad

// function cantidad(){
//   nombre=[]
//   productos.forEach(entrada => {
//     var cantidad = parseInt (entrada.cantidad)
//     if (cantidad <= 10){
//       nombre += `${entrada.nombre},` 
//       Swal.fire({
//         icon: 'warning',
//         title: 'Pocos productos en stock!' ,
//         text: ` Por favor comprar ${ nombre } ` ,
//       })
//     }})
    
// }


//funcion de mostrar los productos con poca cantidad en una tabla
function cantidad() {
  var productosBajosStock = [];

  productos.forEach(entrada => {
    var cantidad = parseInt(entrada.cantidad);
    if (cantidad <= 1000) {
      productosBajosStock.push(entrada);
    }
  });

  if (productosBajosStock.length > 0) {
    // Construir la tabla HTML utilizando DataTables
    var tablaHTML = '<div class="tabla-con-scroll">' +
      '<table id="tablaProductos" class="display">' +
      '<thead>' +
      '<tr>' +
      '<th>Código</th>' +
      '<th>Nombre</th>' +
      '<th>Stock</th>' 
      '</tr>' +
      '</thead>' +
      '<tbody>';

    productosBajosStock.forEach(producto => {
      tablaHTML += '<tr>' +
        '<td>' + producto.codigo + '</td>' +
        '<td>' + producto.nombre + '</td>' +
        '<td>' + producto.cantidad + '</td>' 
        '</tr>';
    });

    tablaHTML += '</tbody></table>' +
    '</div>';

    // Mostrar la tabla DataTable en una alerta Swal.fire
    Swal.fire({
      title: 'Pocos productos en stock!',
      html: tablaHTML, // Incorporar la tabla en el contenido HTML
      icon: 'warning',
      onOpen: function () {
        $('#tablaProductos').DataTable(); // Inicializa el DataTable
        
      }
    });
  }
}


//Precio de los productos automaticamente
function precioAut(){
  id= document.getElementById("txtProducto").value
  ejem=productos.findIndex(prod => prod.id === id)
  document.getElementById("intPrecio").value=productos[ejem].precio
}

//Precio de los productos automaticamente
function precioAuto(){
  id= document.getElementById("txtProducto").value
  ejem=productos.findIndex(prod => prod.id === id)
  document.getElementById("precio").value=productos[ejem].precio
}

//Precio de los productos automaticamente
function UnidadAut(){
  id= document.getElementById("txtProducto").value
  ejem=productos.findIndex(prod => prod.id === id)
  document.getElementById("txtUnidadMedida").value=productos[ejem].unidadMedida
}



document.addEventListener('DOMContentLoaded', function () {
  var precios = document.querySelectorAll('.precio');
  precios.forEach(function (precio) {
      var precio_sinFormato = precio.textContent.trim().replace('$', '');
      var precio_formateado = parseFloat(precio_sinFormato).toLocaleString('es-CO', {
          minimumFractionDigits: 0,
          maximumFractionDigits: 2
      });

      precio.textContent = '$ ' + precio_formateado;
  });
});


