document.addEventListener('DOMContentLoaded', () => {
  // Obtén el elemento de input de tipo "file" y el elemento <img>
  const fileInput = document.getElementById('fileFoto');
  const imagenProducto = document.getElementById('imagenProducto');

  // Verifica si los elementos existen antes de agregar el evento
  if (fileInput && imagenProducto) {
    // Agrega un evento de cambio al input de tipo "file"
    fileInput.addEventListener('change', (event) => {
      const selectedFile = event.target.files[0]; // Obtén el archivo seleccionado

      if (selectedFile) {
        // Crea una URL del archivo seleccionado y establece como src de la imagen
        const imageUrl = URL.createObjectURL(selectedFile);
        imagenProducto.src = imageUrl;
      }
    });
  }
});


  // function modalEliminarUser(userId) {
  //     Swal.fire({
  //       title: '¿Estás seguro?',
  //       text: 'Esta acción Desactiva al usuario. ¿Estás seguro de continuar?',
  //       icon: 'warning',
  //       showCancelButton: true,
  //       confirmButtonColor: '#012e4a',
  //       cancelButtonColor: '#960b0b',
  //       confirmButtonText: 'Aceptar',
  //       cancelButtonText: 'Cancelar'
  //     }).then((result) => {
  //       if (result.isConfirmed) {
  //         eliminarUsuario(userId);
  //       }
  //     });
  //   }



window.addEventListener('load', function() {
  const switchCheckboxes = document.querySelectorAll('#flexSwitchCheckChecked');
  console.log(switchCheckboxes);
  
  switchCheckboxes.forEach(function (switchCheckbox) {
    switchCheckbox.addEventListener('change', function() {
      const userId = this.getAttribute('data-user-id');
      const action = this.checked ? 'Activar' : 'Desactivar';
      console.log(userId);

      Swal.fire({
        title: `¿Estás seguro?`,
        text: `¿Estás seguro de ${action} esta cuenta?`, 
        icon: 'question',
        showCancelButton: true,
        confirmButtonColor: '#012e4a',
        cancelButtonColor: '#960b0b',
        confirmButtonText: `Si, ${action}`,
        cancelButtonText: 'Cancelar',
      }).then((result) => {
        if (result.isConfirmed) {
          if (action === 'Desactivar') {
            const accion = 'Inactivo';
            const url = "/suspendeUsuario/"+userId+"/"+accion+"/";
            console.log(url);  
            
            fetch(url)
              .then((response) => response.json())
              .then((data) => {
                if (data.estado) {
                  Swal.fire({
                    title: 'Gestión Inventario',
                    text: data.mensaje,
                    icon: 'success',
                    confirmButtonColor: '#012e4a',
                    confirmButtonText: 'Aceptar',
                  }).then((result) => {
                    if (result.isConfirmed) {
                      window.location.reload();
                    }
                  });
                } else {
                  Swal.fire({
                    title: 'Gestión Inventario',
                    text: data.mensaje,
                    icon: 'error',
                    confirmButtonText: 'Aceptar',
                  }).then((result) => {
                    if (result.isConfirmed) {
                      window.location.reload();
                    }
                  });
                }
              });
          } else if (action === 'Activar') { // Agregar lógica para el caso de 'Activar'
            const accion = 'Activo';
            const url = "/activaUsuario/"+userId+"/"+accion+"/";
            console.log(url);  
            
            fetch(url)
              .then((response) => response.json())
              .then((data) => {
                if (data.estado) {
                  Swal.fire({
                    title: 'Gestión Inventario',
                    text: data.mensaje,
                    icon: 'success',
                    confirmButtonColor: '#012e4a',
                    confirmButtonText: 'Aceptar',
                  }).then((result) => {
                    if (result.isConfirmed) {
                      window.location.reload();
                    }
                  });
                } else {
                  Swal.fire({
                    title: 'Gestión Inventario',
                    text: data.mensaje,
                    icon: 'error',
                    confirmButtonText: 'Aceptar',
                  }).then((result) => {
                    if (result.isConfirmed) {
                      window.location.reload();
                    }
                  });
                }
              });
          } 
        } else {
          this.checked = !this.checked;
        }
      });
    });
  });
});

  

  // function eliminarUsuario(userId) {
  //   fetch(`/eliminarUsuario/${userId}/`, {
  //     method: 'DELETE',
  //     headers: {
  //       'X-CSRFToken': getCSRFToken() 
  //     }
  //   })
  //     .then(response => response.json())
  //     .then(data => {
  //       if (data.estado) {
  //         Swal.fire({
  //           title: '¡Usuario Desactivado!',
  //           text: data.mensaje,
  //           icon: 'success'
  //         }).then(() => {
  //           location.reload();
  //         });
  //       } else {
  //         Swal.fire({
  //           title: 'Error',
  //           text: data.mensaje,
  //           icon: 'error'
  //         });
  //       }
  //     })
  //     .catch(error => {
  //       Swal.fire({
  //         title: 'Error',
  //         text: 'Ha ocurrido un error al Desactivar el usuario.',
  //         icon: 'error'
  //       });
  //       console.error(error);
  //     });
  // }
  
  function getCSRFToken() {
  const cookieName = 'csrftoken';
  const cookieValue = document.cookie.match('(^|;)\\s*' + cookieName + '\\s*=\\s*([^;]+)');
  return cookieValue ? cookieValue.pop() : '';
  }


  
  function modalEliminarProducto(proCodigo) {
    Swal.fire({
      title: '¿Estás seguro?',
      text: 'Esta acción eliminará al producto. ¿Estás seguro de continuar?',
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#012e4a',
      cancelButtonColor: '#960b0b',
      confirmButtonText: 'Sí, eliminar',
      cancelButtonText: 'Cancelar'
    }).then((result) => {
      if (result.isConfirmed) {
        eliminarProducto(proCodigo);
      }
    });
  }
  

  function eliminarProducto(proCodigo) {
    fetch(`/eliminarProducto/${proCodigo}/`, {
      method: 'DELETE',
      headers: {
        'X-CSRFToken': getCSRFToken() 
      }
    })
      .then(response => response.json())
      .then(data => {
        if (data.estado) {
          Swal.fire({
            title: '¡Eliminado!',
            text: data.mensaje,
            icon: 'success'
          }).then(() => {
            location.reload();
          });
        } else {
          Swal.fire({
            title: 'Error',
            text: data.mensaje,
            icon: 'error'
          });
        }
      })
      .catch(error => {
        Swal.fire({
          title: 'Error',
          text: 'Ha ocurrido un error al eliminar el producto.',
          icon: 'error'
        });
        console.error(error);
      });
  }
  



  function modalEliminarProveedor(proIdentificacion) {
    Swal.fire({
      title: '¿Estás seguro?',
      text: 'Esta acción eliminará al proveedor. ¿Estás seguro de continuar?',
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#012e4a',
      cancelButtonColor: '#960b0b',
      confirmButtonText: 'Sí, eliminar',
      cancelButtonText: 'Cancelar'
    }).then((result) => {
      if (result.isConfirmed) {
        eliminarProveedor(proIdentificacion);
      }
    });
  }


  function eliminarProveedor(proIdentificacion) {
    fetch(`/eliminarProveedor/${proIdentificacion}/`, {
      method: 'DELETE',
      headers: {
        'X-CSRFToken': getCSRFToken() 
      }
    })
    .then(response => response.json())
    .then(data => {
      if (data.estado) {
        Swal.fire({
          title: '¡Eliminado!',
          text: data.mensaje,
          icon: 'success'
        }).then(() => {
          location.reload();
        });
      } else {
        Swal.fire({
          title: 'Error',
          text: data.mensaje,
          icon: 'error'
        });
      }
    })
    .catch(error => {
      Swal.fire({
        title: 'Error',
        text: 'Ha ocurrido un error al eliminar el proveedor.',
        icon: 'error'
      });
      console.error(error);
    });
  }



  function modalEliminarUnidad(uniNombre) {
    Swal.fire({
      title: '¿Estás seguro?',
      text: 'Esta acción eliminará la Unidad. ¿Estás seguro de continuar?',
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#012e4a',
      cancelButtonColor: '#960b0b',
      confirmButtonText: 'Sí, eliminar',
      cancelButtonText: 'Cancelar'
    }).then((result) => {
      if (result.isConfirmed) {
        eliminarUnidad(uniNombre);
      }
    });
  }

  function eliminarUnidad(uniNombre) {
    fetch(`/eliminarUnidad/${uniNombre}/`, {
      method: 'DELETE',
      headers: {
        'X-CSRFToken': getCSRFToken() 
      }
    })
      .then(response => response.json())
      .then(data => {
        if (data.estado) {
          Swal.fire({
            title: '¡Eliminado!',
            text: data.mensaje,
            icon: 'success'
          }).then(() => {
            location.reload();
          });
        } else {
          Swal.fire({
            title: 'Error',
            text: data.mensaje,
            icon: 'error'
          });
        }
      })
      .catch(error => {
        Swal.fire({
          title: 'Error',
          text: 'Ha ocurrido un error al eliminar la Unidad.',
          icon: 'error'
        });
        console.error(error);
      });
  }


  function modalEliminarMarca(marcaNombre) {
    Swal.fire({
      title: '¿Estás seguro?',
      text: 'Esta acción eliminará la Marca. ¿Estás seguro de continuar?',
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#012e4a',
      cancelButtonColor: '#960b0b',
      confirmButtonText: 'Sí, eliminar',
      cancelButtonText: 'Cancelar'
    }).then((result) => {
      if (result.isConfirmed) {
        eliminarMarca(marcaNombre);
      }
    });
  }

  function eliminarMarca(marcaNombre) {
    fetch(`/eliminarMarca/${marcaNombre}/`, {
      method: 'DELETE',
      headers: {
        'X-CSRFToken': getCSRFToken() 
      }
    })
      .then(response => response.json())
      .then(data => {
        if (data.estado) {
          Swal.fire({
            title: '¡Eliminado!',
            text: data.mensaje,
            icon: 'success'
          }).then(() => {
            location.reload();
          });
        } else {
          Swal.fire({
            title: 'Error',
            text: data.mensaje,
            icon: 'error'
          });
        }
      })
      .catch(error => {
        Swal.fire({
          title: 'Error',
          text: 'Ha ocurrido un error al eliminar la Marca.',
          icon: 'error'
        });
        console.error(error);
      });
  }





function confirmarCambioContrasena(userId) {
    Swal.fire({
        title: 'Cambiar Contraseña',
        text: '¿Está seguro de que desea cambiar la contraseña? La sesión se cerrará.',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#012e4a',
        cancelButtonColor: '#960b0b',
        confirmButtonText: 'Sí, cambiar contraseña',
        cancelButtonText: 'Cancelar',
    }).then((result) => {
        if (result.isConfirmed) {
            // Si el usuario confirmó, ejecuta la función para cambiar la contraseña
            guardarContra();
        }
    });
}

  
function cambiarContra(usuarioId) {
  // Configura el formulario de cambio de contraseña
  document.getElementById("contraActual").value = "";
  document.getElementById("nuevaContra").value = "";
  document.getElementById("confirmarContra").value = "";

  // Actualiza el valor del campo oculto con el ID del usuario
  document.getElementById("idUsuario").value = usuarioId;
}



function guardarContra() {
    const contraActual = document.getElementById("contraActual").value;
    const nuevaContra = document.getElementById("nuevaContra").value;
    const confirmarContra = document.getElementById("confirmarContra").value;
    const userId = document.getElementById("idUsuario").value;

    // Realiza validaciones de contraseñas aquí
    if (nuevaContra !== confirmarContra) {
      Swal.fire("Error", "Las contraseñas no coinciden", "error");
      return;
    }
    
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    // Aquí puedes usar AJAX o Fetch para enviar la solicitud al servidor
    $.ajax({
      type: "POST",
      url: "/actualizarContraseña/",  // Asegúrate de usar la URL correcta
      data: {
          idUsuario: userId,
          contraActual: contraActual,
          nuevaContra: nuevaContra,
          confirmarContra: confirmarContra,
          csrfmiddlewaretoken: csrfToken  // Añade el token CSRF
      },
      success: function(response) {
        if (response.mensaje === "Contraseña actualizada correctamente") {
            Swal.fire("Éxito", response.mensaje, "success")
            .then(() => {
                $('#modalContra').modal('hide');
                window.location.href = "/";  // Redirige al inicio
            });
        } else {
            Swal.fire("Error", response.mensaje, "error");
        }
      },
      error: function(xhr, status, error) {
          Swal.fire("Error", "Hubo un error al procesar la solicitud", "error");
          console.log(xhr.responseText);
      }
  });
}