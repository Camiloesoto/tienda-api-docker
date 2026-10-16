from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from .domain.builders import OrdenBuilder
from .domain.logic import CalculadorImpuestos
from .models import Inventario, Libro


class CompraService:
    def __init__(self, procesador_pago):
        self.procesador = procesador_pago
        self.builder = OrdenBuilder()

    def obtener_detalle_producto(self, libro_id):
        libro = get_object_or_404(Libro, id=libro_id)
        total = CalculadorImpuestos.obtener_total_con_iva(libro.precio)
        return {"libro": libro, "total": total}

    def ejecutar_proceso_compra(self, usuario, lista_productos, direccion):
        cantidades = {}
        unicos = {}
        for producto in lista_productos:
            cantidades[producto.id] = cantidades.get(producto.id, 0) + 1
            unicos[producto.id] = producto

        for libro_id, qty in cantidades.items():
            inv = Inventario.objects.get(libro=unicos[libro_id])
            if inv.cantidad < qty:
                raise ValueError("No hay existencias.")

        # Uso del Builder: Semantica clara y validacion interna
        orden = (
            self.builder
            .con_usuario(usuario)
            .con_productos(lista_productos)
            .para_envio(direccion)
            .build()
        )

        # Uso del Factory (inyectado): Cambio de comportamiento sin cambio de codigo
        if self.procesador.pagar(orden.total):
            for libro_id, qty in cantidades.items():
                inv = Inventario.objects.get(libro=unicos[libro_id])
                inv.cantidad -= qty
                inv.save()
            return f"Orden {orden.id} procesada exitosamente."

        orden.delete()
        raise Exception("Error en la pasarela de pagos.")

    def ejecutar_compra(self, libro_id, cantidad=1, direccion="", usuario=None):
        libro = get_object_or_404(Libro, id=libro_id)
        if usuario is None:
            usuario = get_user_model().objects.get_or_create(username="camilo_soto")[0]

        inv = get_object_or_404(Inventario, libro=libro)
        if inv.cantidad < cantidad:
            raise ValueError("No hay suficiente stock para completar la compra.")

        mensaje = self.ejecutar_proceso_compra(
            usuario=usuario,
            lista_productos=[libro] * cantidad,
            direccion=direccion,
        )
        return mensaje


class CompraRapidaService:
    def __init__(self, procesador_pago):
        self.procesador_pago = procesador_pago
        self.builder = OrdenBuilder()

    def obtener_detalle(self, libro_id):
        libro = get_object_or_404(Libro, id=libro_id)
        total = CalculadorImpuestos.obtener_total_con_iva(libro.precio)
        return {"libro": libro, "total": total}

    def procesar(self, libro_id, usuario=None, direccion="Medellin"):
        if usuario is None:
            usuario = get_user_model().objects.get_or_create(username="camilo_soto")[0]

        servicio = CompraService(procesador_pago=self.procesador_pago)
        mensaje = servicio.ejecutar_proceso_compra(
            usuario=usuario,
            lista_productos=[Libro.objects.get(id=libro_id)],
            direccion=direccion,
        )
        return mensaje
