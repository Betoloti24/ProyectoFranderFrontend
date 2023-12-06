document.getElementById('login-form').addEventListener('submit', function(event) {
    event.preventDefault();

    let email = document.getElementById('email').value;
    let password = document.getElementById('password').value;

    // Realiza la validación del usuario y la contraseña aquí.
    console.log('Email:', email);
    console.log('Password:', password);
});
