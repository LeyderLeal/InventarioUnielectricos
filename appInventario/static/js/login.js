// login.js

// Función para mostrar u ocultar la contraseña
function VisibleContraseña() {
    var passwordField = document.getElementById("txtPassword");
    var toggleIcon = document.getElementById("togglePassword");

    if (passwordField.type === "password") {
        passwordField.type = "text";
        toggleIcon.className = "fas fa-eye";
    } else {
        passwordField.type = "password";
        toggleIcon.className = "fas fa-eye-slash";
    }
}

// Configurar reCAPTCHA v3
grecaptcha.ready(function () {
    grecaptcha.execute('6LdrUQ4oAAAAADDPgekD1XJsUYBwUdrYdpAEYrSN', { action: '/loginX/' }).then(function (token) {
        document.getElementById('g-recaptcha-response').value = token;
    });
});