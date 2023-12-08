from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
import requests

def login(request):
    # declaramos el context
    context = {
        "error": False,
        "cambio": False,
        "mensaje": "",
        "data": {}
    }

    if request.method == "POST":
        # Obtén los datos del formulario (puedes obtenerlos de request.POST)
        datos_formulario = {
            'correo': request.POST['email'],
            'clave': request.POST['password'],
        }
        # Construye un diccionario con los archivos adjuntos (imágenes)
        # archivos = {'imagen': request.FILES['imagen']}
        # response = requests.post(url_api, data=datos_formulario, files=archivos)

        # Realiza la solicitud POST a tu API
        url_api = 'http://127.0.0.1:8000/usuarios/inicio_sesion/'
        response = requests.get(url_api, data=datos_formulario)

        # Verifica el resultado de la solicitud
        if response.status_code == 200:
            # La solicitud fue exitosa
            url = str(reverse_lazy("index"))
            http = HttpResponseRedirect(url)
            http.set_cookie('usuario', response.json().get('data').get('cedula'))
            return http
        
        # capturamos el posible error
        context = {
            "error": response.json()["error"],
            "cambio": False,
            "mensaje": response.json()["mensaje"],
            "data": response.json()["data"],
        }
        
    # verificamos si hay un mensaje en las cookies
    if (request.COOKIES.get("mensaje", None)):
        context = {
            "error": False,
            "cambio": True,
            "mensaje": request.COOKIES.get("mensaje"),
            "data": {}
        }
    
    # eliminamos las cookies si las hubo
    http = render(request, "login.html", context=context)
    if context["cambio"]:
        http.delete_cookie("mensaje")  
        
    return http

def registro(request):
    context = {
        "error": False,
        "mensaje": [],
        "data": {}
    }
    
    if request.method == "POST":
        clave = request.POST['clave_acceso']
        veri_clave = request.POST['confirm_password']
        
        if (clave == veri_clave):
            # Obtén los datos del formulario (puedes obtenerlos de request.POST)
            datos_formulario = {
                'cedula': request.POST['cedula'],
                'nombre': request.POST['nombre'],
                'apellido': request.POST['apellido'],
                'f_nacimiento': request.POST['f_nacimiento'],
                'genero': request.POST['genero'],
                'telefono': request.POST['telefono'],
                'correo': request.POST['correo'],
                'clave_acceso': request.POST['clave_acceso'],
            }
            
            # Realiza la solicitud POST a tu API
            url_api = 'http://127.0.0.1:8000/usuarios/registro/'
            response = requests.post(url_api, data=datos_formulario)
            
            # Verifica el resultado de la solicitud
            if response.status_code == 201:
                # La solicitud fue exitosa
                url = str(reverse_lazy("index"))
                http = HttpResponseRedirect(url)
                http.set_cookie('usuario', datos_formulario.get('cedula'))
                return http
            
            # capturamos el posible error
            mensaje = [response.json()["mensaje"]]
            data = response.json()["data"]
            if (data):
                mensaje.extend([f"{key.upper()}: {value[0]}" for key, value in data.items()])
            context = {
                "error": response.json()["error"],
                "mensaje": mensaje,
                "data": data,
            }
        else:
            context = {
                "error": True,
                "mensaje": ["Las contraseñas no coinciden"],
                "data": {}
            }
    len(context)
    
    return render(request, "register.html", context=context)

def cambio_clave(request):
    # declaramos el context
    context = {
        "error": False,
        "mensaje": "",
        "data": {}
    }
    
    if request.method == "POST":
        # extraemos los datos
        datos_formulario = {
            'correo': request.POST['email'],
            'nueva_clave': request.POST['password'],
        }
        
        # realizmos la solicitud
        url_api = 'http://127.0.0.1:8000/usuarios/cambiar_clave/'
        response = requests.put(url_api, data=datos_formulario)
        
        if response.status_code == 200:
            # La solicitud fue exitosa
            url = str(reverse_lazy("login"))
            http = HttpResponseRedirect(url)
            http.set_cookie("mensaje", "Cambio de clave exitoso")
            return http
        
        context = {
            "error": True,
            "mensaje": response.json()["mensaje"],
            "data": {}
        }
    
    return render(request, "cambio_clave.html", context=context)

# vista principal
def index(request):
    return render(request, "index.html")

# vista perfil
def perfil(request):

    context = {
        'mensaje': None
    }

    # actualizamos las preferencias si se envia una peticion
    if request.method == 'POST':
        # obtenemos las preferencias
        preferencias = list(map(lambda x: int(x), request.POST.getlist('categoria')))
        # guardamos las preferencias
        datos = {
            'preferencias': preferencias
        }
        url_api = f'http://127.0.0.1:8000/usuarios/cambiar_preferencias/{request.COOKIES.get("usuario")}/'
        response = requests.put(url_api, data=datos)
        context['mensaje'] = response.json().get('mensaje')

    # realizmos la solicitud
    url_api = f'http://127.0.0.1:8000/usuarios/{request.COOKIES.get("usuario")}/'
    response = requests.get(url_api)
    data_usuario = response.json().get('data')
    
    # creamos el contexto
    context.update(data_usuario)

    # consultamos las categorias
    url_api = f'http://127.0.0.1:8000/categorias/'
    response = requests.get(url_api)
    list_categorias = response.json().get('data')

    # definimos el contexto
    context['categorias'] = list_categorias

    # context = 
    return render(request, "profile.html", context=context)

# vista carrito
def carrito(request):
    
    return render(request, "carrito.html")

# vista facturas
def facturas(request):
    # consultamos el usuario
    url_api = f'http://127.0.0.1:8000/usuarios/{request.COOKIES["usuario"]}/'
    response = requests.get(url_api)
    usuario = response.json().get('data')

    # vemos las facturas del usuario
    url_api = f'http://127.0.0.1:8000/facturas/{request.COOKIES["usuario"]}/'
    response = requests.get(url_api)
    list_facturas = response.json().get('data')

    # creamos el context
    context = usuario
    context['facturas'] = list_facturas

    return render(request, "facturas.html", context=context)