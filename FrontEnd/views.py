from django.shortcuts import render
from django.http import HttpResponse
import requests

def index(request):
    if request.method == "POST":
        # Obtén los datos del formulario (puedes obtenerlos de request.POST)
        datos_formulario = {
            'nombre': request.POST['nombre'],
            'precio_venta': request.POST['precio_venta'],
            'marca': request.POST['marca'],
            'genero': request.POST['genero'],
            'categorias': [int(x) for x in request.POST['categoria']],
            # Otros campos del formulario
        }
        # Construye un diccionario con los archivos adjuntos (imágenes)
        archivos = {'imagen': request.FILES['imagen']}

        print(datos_formulario, archivos)
        # Realiza la solicitud POST a tu API
        url_api = 'http://127.0.0.1:8000/ropas/'
        response = requests.post(url_api, data=datos_formulario, files=archivos)
        
        # Imprimimos el cuerpo del response
        print(response.text)
        # Verifica el resultado de la solicitud
        if response.status_code == 201:
            # La solicitud fue exitosa
            return HttpResponse('Formulario enviado correctamente')
        else:
            # La solicitud no fue exitosa
            return HttpResponse('Error al enviar el formulario')

    return render(request, "index.html")