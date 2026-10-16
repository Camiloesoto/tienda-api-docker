from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views import View

from .infra.factories import PaymentFactory
from .models import Libro
from .services import CompraRapidaService, CompraService


def _usuario_compra(request):
    if request.user.is_authenticated:
        return request.user
    User = get_user_model()
    usuario, _ = User.objects.get_or_create(
        username="camilo_soto",
        defaults={"first_name": "Camilo", "last_name": "Soto"},
    )
    return usuario


class CatalogoView(View):
    template_name = 'tienda_app/catalogo.html'

    def get(self, request):
        libros = Libro.objects.select_related('inventario').all()
        return render(request, self.template_name, {'libros': libros})


class CompraView(View):
    """
    Vista agnostica: no sabe que banco se usa, solo sabe que la
    fabrica le entrega un procesador que funciona.
    """

    template_name = 'tienda_app/compra.html'

    def setup_service(self):
        # ANTES: gateway = BancoNacionalProcesador()
        # AHORA: Delegacion total a la Fabrica
        gateway = PaymentFactory.get_processor()
        return CompraService(procesador_pago=gateway)

    def get(self, request, libro_id):
        servicio = self.setup_service()
        contexto = servicio.obtener_detalle_producto(libro_id)
        return render(request, self.template_name, contexto)

    def post(self, request, libro_id):
        servicio = self.setup_service()
        libro = get_object_or_404(Libro, id=libro_id)
        direccion = request.POST.get('direccion', 'Calle 123 - Medellin')
        try:
            mensaje = servicio.ejecutar_proceso_compra(
                usuario=_usuario_compra(request),
                lista_productos=[libro],
                direccion=direccion,
            )
            return render(
                request,
                self.template_name,
                {
                    'mensaje_exito': mensaje,
                    'libro': libro,
                },
            )
        except (ValueError, Exception) as e:
            contexto = servicio.obtener_detalle_producto(libro_id)
            contexto['error'] = str(e)
            return render(request, self.template_name, contexto, status=400)


class CompraRapidaView(View):
    template_name = 'tienda_app/compra_rapida.html'

    def setup_service(self):
        gateway = PaymentFactory.get_processor()
        return CompraRapidaService(procesador_pago=gateway)

    def get(self, request, libro_id):
        contexto = self.setup_service().obtener_detalle(libro_id)
        return render(request, self.template_name, contexto)

    def post(self, request, libro_id):
        try:
            mensaje = self.setup_service().procesar(
                libro_id,
                usuario=_usuario_compra(request),
            )
            return HttpResponse(mensaje)
        except (ValueError, Exception) as e:
            return HttpResponse(str(e), status=400)
