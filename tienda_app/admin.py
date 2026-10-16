from django.contrib import admin

from .models import Inventario, Libro, Orden


@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    list_display = ("titulo", "precio")


@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):
    list_display = ("libro", "cantidad")


@admin.register(Orden)
class OrdenAdmin(admin.ModelAdmin):
    list_display = ("libro", "total", "fecha_creacion")
