from decimal import Decimal, ROUND_HALF_UP

from ..models import Orden


class OrdenBuilder:
    def __init__(self):
        self.reset()

    def reset(self):
        self._usuario = None
        self._items = []
        self._direccion = ""

    def con_usuario(self, usuario):
        self._usuario = usuario
        return self

    def con_productos(self, productos):
        self._items = list(productos)
        return self

    def para_envio(self, direccion):
        self._direccion = direccion
        return self

    def build(self) -> Orden:
        if not self._usuario or not self._items:
            raise ValueError("Datos insuficientes para crear la orden.")

        subtotal = sum(Decimal(str(p.precio)) for p in self._items)
        total_con_iva = (subtotal * Decimal("1.19")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        orden = Orden.objects.create(
            usuario=self._usuario,
            libro=self._items[0],
            total=total_con_iva,
            direccion_envio=self._direccion,
        )
        self.reset()
        return orden
