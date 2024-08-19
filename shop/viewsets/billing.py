from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from shop.models import Cart, Invoice, InvoiceItem
from shop.serializers import InvoiceSerializer
from shop.utils import is_authenticate


class BillingViewSet(viewsets.ViewSet):
    serializer_class = InvoiceSerializer

    @action(
        detail=False,
        methods=["get"],
        url_path="generate",
    )
    def generate_invoice(self, request):
        if not is_authenticate(request):
            return Response(
                {
                    "detail": "Authentication credentials were not provided OR May be deleted User."
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )
        cart = get_object_or_404(Cart, user=request.user)
        if cart.cartitem_set.count() == 0:
            return Response(
                {"detail": "Cart is empty after created invoice"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        total_price = cart.get_total_price()
        total_discount = cart.get_total_discount()
        final_amount = total_price - total_discount

        invoice = Invoice.objects.create(
            user=request.user,
            total_price=total_price,
            total_discount=total_discount,
            final_amount=final_amount,
        )

        for item in cart.cartitem_set.all():
            InvoiceItem.objects.create(
                invoice=invoice,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
                discount=item.product.discount,
                total_price=item.get_total_price(),
            )

        cart.cartitem_set.all().delete()  # Clear the cart after generating the invoice

        serializer = InvoiceSerializer(invoice)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"], url_path="detail")
    def view_invoice(self, request, pk=None):
        if not is_authenticate(request):
            return Response(
                {
                    "detail": "Authentication credentials were not provided OR May be deleted User."
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )
        invoice = get_object_or_404(Invoice, pk=pk, user=request.user)
        serializer = InvoiceSerializer(invoice)
        return Response(serializer.data)
