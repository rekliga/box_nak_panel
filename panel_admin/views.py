from django.contrib.auth.decorators import login_required
import json
from authlib.integrations.django_client import OAuth
from django.conf import settings
from django.shortcuts import redirect, render, redirect
from django.urls import reverse
from urllib.parse import quote_plus, urlencode

import requests
from .forms import ProductoForm

oauth = OAuth()

url = settings.URL_BACKEND

oauth.register(
    "auth0",
    client_id=settings.AUTH0_CLIENT_ID,
    client_secret=settings.AUTH0_CLIENT_SECRET,
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f"https://{settings.AUTH0_DOMAIN}/.well-known/openid-configuration",
)


def login(request):
    return oauth.auth0.authorize_redirect(
        request, request.build_absolute_uri(reverse("callback"))
    )


def callback(request):
    token = oauth.auth0.authorize_access_token(request)
    request.session["user"] = token
    
    if token:
        # Guarda la información del usuario en la sesión
        request.session["user"] = {
            "name": token["userinfo"].get("name"),
            "picture": token["userinfo"].get("picture"),
            "id_token": token["id_token"],
        }
    
    return redirect(reverse("home"))

def home(request):
    user = request.session.get("user")
    
    if not user:
        return redirect(reverse("login"))  # Redirige si no hay usuario autenticado
    
    return render(request, "home.html", {"user": user})

def logout(request):
    request.session.clear()

    return redirect(
        f"https://{settings.AUTH0_DOMAIN}/v2/logout?"
        + urlencode(
            {
                "returnTo": request.build_absolute_uri(reverse("index")),
                "client_id": settings.AUTH0_CLIENT_ID,
            },
            quote_via=quote_plus,
        ),
    )


def index(request):
    return render(
        request,
        "index.html",
        context={
            "session": request.session.get("user"),
            "pretty": json.dumps(request.session.get("user"), indent=4),
        },
    )


def crear_producto(request):
    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            # Extraer datos del formulario
            nombre = form.cleaned_data["nombre"]
            descripcion = form.cleaned_data["descripcion"]
            categoria = form.cleaned_data["categoria"]
            precio = form.cleaned_data["precio"]
            stock = form.cleaned_data["stock"]
            imagen = form.cleaned_data.get("imagen")  # Archivo a subir

            # Encabezados para autorización
            headers = {"Authorization": f"Bearer {request.session['user']['id_token']}"}
            
            # Archivo para enviar en multipart/form-data
            files = {
                "archivo": (
                    imagen.name,
                    imagen,
                    imagen.content_type,
                )  # Nombre, contenido, tipo MIME
            }

            try:
                # Realizar la solicitud PUT al endpoint
                response = requests.put(
                    url=f"{url}/posts/media/upload",
                    headers=headers,
                    files=files,  # Envía el archivo como multipart/form-data
                )
                response = response.json()
                data = {
                    "name": nombre,
                    "description": descripcion,
                    "price": float(precio),
                    "stock": stock,
                    "category": categoria,
                    "image_url": response["data"]["url"],
                }

                cargar_producto = requests.post(
                    json=data,
                    headers=headers,
                    url=f"{url}/products/create",
                )
                
                # Verifica errores HTTP
            except Exception as e:
                
                print(f"Error al subir el archivo: {e}")
                return render(
                    request,
                    "crear_producto.html",
                    {
                        "form": form,
                        "error": "Hubo un problema al subir el archivo. Inténtalo de nuevo.",
                    },
                )

            # Si todo es exitoso
            return redirect("productos_gracias")
    else:
        form = ProductoForm()

    return render(request, "crear_producto.html", {"form": form})


def productos_gracias(request):
    return render(request, "productos_gracias.html")


def lista_productos(request):
    
    headers = {"Authorization": f"Bearer {request.session['user']['id_token']}"}
    response = requests.get(
        f"{url}/products/get/all", headers=headers
    )
    response = response.json()["data"]["result"]
    return render(request, "lista_productos.html", {"productos": response})
