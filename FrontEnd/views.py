from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from .functions import segmentar
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
    # definimos el contexto
    context = {}
    
    # consultamos todos los productos
    ## todos los productos
    url_api = 'http://127.0.0.1:8000/ropas/'
    response = requests.get(url_api)
    products = response.json().get('data')
    ## recomendaciones por preferencias
    url_api = f'http://127.0.0.1:8000/recomendaciones/preferencias_usuario/{request.COOKIES.get("usuario")}/'
    response = requests.get(url_api)
    products_preferencias = response.json().get('data')
    ## recomendaciones de otros usuarios
    url_api = f'http://127.0.0.1:8000/recomendaciones/preferencias_otros_usuario/{request.COOKIES.get("usuario")}/'
    response = requests.get(url_api)
    products_preferencias_otros_usuarios = response.json().get('data')
    ## recomendaciones de prendas mas vendidas
    url_api = f'http://127.0.0.1:8000/recomendaciones/prendas_mas_vendidas/'
    response = requests.get(url_api)
    products_mas_vendidos = response.json().get('data')
        
    if request.method == 'POST':
        try: 
            # extraemos los datos
            cantidad = request.POST['cantidad']
            id_ropa = request.POST['agregar']
            datos_formulario = {
                "cantidad": int(cantidad),
                "id_usuario": request.COOKIES.get("usuario"),
                "id_ropa": int(id_ropa)
            }
            
            # agregamos al carrito
            url_api = 'http://127.0.0.1:8000/carritos/'
            response = requests.post(url_api, data=datos_formulario)
            
            if response.status_code == 201:
                context['mensaje'] = response.json().get('mensaje')
            else:
                # actualizamos la cantidad
                datos_formulario.pop('id_usuario')
                url_api = f'http://127.0.0.1:8000/carritos/{request.COOKIES.get("usuario")}/'
                response = requests.put(url_api, data=datos_formulario)
                context['mensaje'] = response.json().get('mensaje')
        except Exception as e:
            context['error'] = "Ingrese una cantidad para agregar en el carrito"
        
    # dividimos la lista de productos en segmentos de 4
    products = segmentar(4, products)
    context['list_products'] = products
    
    # dividimos la lista de productos recomendados por las preferencias en segmentos de 4
    if products_preferencias:
        products_preferencias = segmentar(4, products_preferencias)
        context['list_products_preferences'] = products_preferencias
    
    # dividimos la lista de productos recomendados por otros usuarios en segmentos de 4
    if products_preferencias_otros_usuarios:
        products_preferencias_otros_usuarios = segmentar(4, products_preferencias_otros_usuarios)
        context['list_products_preferences_others_user'] = products_preferencias_otros_usuarios
    
    # dividimos la lista de productos mas recomendados en segmentos de 4
    if products_mas_vendidos:
        products_mas_vendidos = segmentar(4, products_mas_vendidos)
        context['list_products_mas_vendidos'] = products_mas_vendidos

    return render(request, "index.html", context=context)

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
    # declaramos el contexto
    context = {}
    
    # validamos las peticiones
    if request.method == 'POST':
        if request.POST.get('pagar', None) is not None:
            print(request.POST.get('pagar', None))
            # pagamos el carrito del usuario
            url_api = f'http://127.0.0.1:8000/carritos/pagar/{request.COOKIES.get("usuario")}/'
            response = requests.put(url_api)
            context['mensaje'] = response.json().get('mensaje')
        elif request.POST.get('eliminar', None):
            # eliminamos un producto del carrito
            id_ropa = request.POST['eliminar']
            url_api = f'http://127.0.0.1:8000/carritos/{request.COOKIES.get("usuario")}/{id_ropa}/'
            response = requests.delete(url_api)
            context['mensaje'] = response.json().get('mensaje')
            
            
            
    # consultamos el carrito del usuario
    url_api = f'http://127.0.0.1:8000/carritos/{request.COOKIES["usuario"]}/'
    response = requests.get(url_api)
    list_carrito = response.json().get('data')
    # consultamos los productos
    url_api = f'http://127.0.0.1:8000/ropas/'
    response = requests.get(url_api)
    list_producto = response.json().get('data') 
    
    # calculamos los totales y guardamos los productos
    total = 0
    carrito = []
    for item in list_carrito:
        producto = list(filter(lambda x: x.get('id') == item.get('id_ropa'), list_producto))[0]
        producto['cantidad'] = item.get('cantidad')
        producto['subtotal'] = float(producto.get('precio_venta')) * producto.get('cantidad')
        total += producto.get('subtotal')
        carrito.append(producto)
    context['total'] = total
    
    # dividimos el carrito en segmentos de 4
    if carrito:
        carrito = segmentar(4, carrito)
    context['carrito'] = carrito
    
    return render(request, "carrito.html", context=context)

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