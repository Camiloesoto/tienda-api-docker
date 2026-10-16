import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Tienda.settings")
django.setup()

from django.contrib.auth import get_user_model

from tienda_app.models import Inventario, Libro

User = get_user_model()
User.objects.get_or_create(
    username="camilo_soto",
    defaults={"first_name": "Camilo", "last_name": "Soto"},
)

libros = [
    ("Clean Code en Python", 150.0, 10),
    ("Arquitectura Limpia", 180.0, 8),
    ("Django Design Patterns", 120.0, 6),
]
for titulo, precio, stock in libros:
    libro, _ = Libro.objects.get_or_create(titulo=titulo, defaults={"precio": precio})
    Inventario.objects.update_or_create(libro=libro, defaults={"cantidad": stock})

print("LIBROS:")
for libro in Libro.objects.all():
    try:
        inventario = libro.inventario
    except Inventario.DoesNotExist:
        inventario = Inventario.objects.create(libro=libro, cantidad=5)
    print(f"  id={libro.id} {libro.titulo} ${libro.precio} stock={inventario.cantidad}")
