from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from shop.models import Cart, CartItem, Product
from shop.serializers import (
    CartItemProductSerializer,
    CartItemSerializer,
    CartProductQuantity,
    CartSerializer,
)
from shop.utils import is_authenticate


class CartViewSet(
    viewsets.GenericViewSet,
):
    pagination_class = LimitOffsetPagination
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    @action(detail=False, methods=["get"], url_path="view")
    def view_cart(self, request):
        if not is_authenticate(request):
            return Response(
                {
                    "detail": "Authentication credentials were not provided OR May be deleted User."
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(
        methods=["post"],
        detail=False,
        name="add_to_cart",
        serializer_class=CartItemProductSerializer,
    )
    def add_to_cart(self, request):
        if not is_authenticate(request):
            return Response(
                {
                    "detail": "Authentication credentials were not provided OR May be deleted User."
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )
        serializer = CartItemProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = get_object_or_404(
            Product, pk=serializer.validated_data["product"]["id"]
        )
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += 1
            cart_item.save()
        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["delete"],
        url_path="remove_product",
        serializer_class=CartProductQuantity,
    )
    def remove_from_cart(self, request):
        if not is_authenticate(request):
            return Response(
                {
                    "detail": "Authentication credentials were not provided OR May be deleted User."
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )
        serializer = CartItemProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = get_object_or_404(
            Product, pk=serializer.validated_data["product"]["id"]
        )
        cart = get_object_or_404(Cart, user=request.user)
        cart_item = get_object_or_404(CartItem, cart=cart, product=product)
        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=["patch"],
        url_path="update-quantity",
        serializer_class=CartProductQuantity,
    )
    def update_cart_item(self, request):
        if not is_authenticate(request):
            return Response(
                {
                    "detail": "Authentication credentials were not provided OR May be deleted User."
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )
        serializer = CartProductQuantity(data=request.data)
        serializer.is_valid(raise_exception=True)
        quantity = serializer.validated_data["quantity"]
        product_id = serializer.validated_data["product_id"]
        product = get_object_or_404(Product, pk=product_id)
        cart = get_object_or_404(Cart, user=request.user)
        cart_item = get_object_or_404(CartItem, cart=cart, product=product)
        cart_item.quantity = int(quantity)
        if cart_item.quantity <= 0:
            cart_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            cart_item.save()
        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data)
