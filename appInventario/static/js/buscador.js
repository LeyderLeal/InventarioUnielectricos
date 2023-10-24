$(document).ready(function () {
    // Captura el evento de clic en el botón de búsqueda
    $("#searchButton").click(function () {
        var searchTerm = $("#searchInput").val().toLowerCase(); // Obtiene el término de búsqueda

        // Itera a través de las ventas y muestra u oculta según el término de búsqueda
        $(".custom-table").each(function () {
            var venta = $(this).text().toLowerCase();
            if (venta.indexOf(searchTerm) === -1) {
                $(this).hide();
            } else {
                $(this).show();
            }
        });
    });
});


document.addEventListener("DOMContentLoaded", function () {
  const txtBusqueda = document.getElementById("txtBusqueda");
  const txtProducto = document.getElementById("txtProducto");

  if (txtBusqueda && txtProducto) {
      const opciones = Array.from(txtProducto.options); // Convierte las opciones en un array para facilitar la búsqueda

      txtBusqueda.addEventListener("input", function () {
          const filtro = txtBusqueda.value.toLowerCase();
          const opcionesFiltradas = opciones.filter((opcion) =>
              opcion.text.toLowerCase().includes(filtro)
          );

          txtProducto.innerHTML = ""; // Borra todas las opciones actuales

          // Agrega las opciones filtradas al menú desplegable
          opcionesFiltradas.forEach((opcion) => {
              txtProducto.appendChild(opcion.cloneNode(true));
          });
      });
  }
});