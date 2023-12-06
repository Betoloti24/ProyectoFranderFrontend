from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
import requests
# Importamos el revace_lacy


def login(request):
    # declaramos el context
    context = {
        "error": False,
        "mensaje": "",
        "data": {}
    }
    
    if request.method == "POST":
        # Obtén los datos del formulario (puedes obtenerlos de request.POST)
        datos_formulario = {
            'correo': request.POST['email'],
            'clave': request.POST['password'],
        }
        # # Construye un diccionario con los archivos adjuntos (imágenes)
        # archivos = {'imagen': request.FILES['imagen']}
        # response = requests.post(url_api, data=datos_formulario, files=archivos)

        # print(datos_formulario, archivos)
        # Realiza la solicitud POST a tu API
        url_api = 'http://127.0.0.1:8000/usuarios/inicio_sesion/'
        response = requests.get(url_api, data=datos_formulario)
        print(response.json())
        # Verifica el resultado de la solicitud
        if response.status_code == 200:
            # La solicitud fue exitosa
            return HttpResponse('Formulario enviado correctamente')
        
        # La solicitud no fue exitosa
        
        context = {
            "error": response.json()["error"],
            "mensaje": response.json()["mensaje"],
            "data": response.json()["data"],
        }

    return render(request, "login.html", context=context)

def registro(request):
    context = {
        "error": False,
        "mensaje": "",
        "data": {}
    }
    
    if request.method == "POST":
        clave = request.POST['password']
        veri_clave = request.POST['confirm_password']
        
        if (clave == veri_clave):
            # Obtén los datos del formulario (puedes obtenerlos de request.POST)
            datos_formulario = {
                'correo': request.POST['email'],
                'clave': request.POST['password'],
                'clave': request.POST['password'],
                'clave': request.POST['password'],
            }
        else:
            context = {
                "error": True,
                "mensaje": "Las contraseñas no coinciden",
                "data": {}
            }
    
    return render(request, "register.html", context=context)

def cambio_clave(request):
    # declaramos el context
    context = {
        "error": False,
        "mensaje": "",
        "data": {}
    }
    
    return render(request, "cambio_clave.html", context=context)