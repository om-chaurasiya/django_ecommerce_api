from rest_framework import serializers

from .models import Cart, CartItem, Invoice, InvoiceItem, Product


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class UserRegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField(required=False)
    password = serializers.CharField()
    password_again = serializers.CharField()


from rest_framework import serializers

from shop.models import User


class UserUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    password_again = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "password", "password_again"]

    def validate(self, data):
        if "password" in data and "password_again" in data:
            if data["password"] != data["password_again"]:
                raise serializers.ValidationError({"password": "Passwords must match."})
        return data

    def update(self, instance, validated_data):
        if "password" in validated_data:
            instance.set_password(validated_data["password"])
            validated_data.pop("password")
            validated_data.pop("password_again")
        return super().update(instance, validated_data)


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "price", "discount"]


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = CartItem
        fields = ["id", "product", "quantity", "get_total_price", "get_total_discount"]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, source="cartitem_set")

    class Meta:
        model = Cart
        fields = ["id", "user", "items", "get_total_price", "get_total_discount"]


class InvoiceItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = InvoiceItem
        fields = ["id", "product", "quantity", "price", "discount", "total_price"]


class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True, source="invoiceitem_set")

    class Meta:
        model = Invoice
        fields = [
            "id",
            "user",
            "created_at",
            "total_price",
            "total_discount",
            "final_amount",
            "items",
        ]


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "price", "discount"]


class CartItemProductSerializer(serializers.ModelSerializer):
    product_id = serializers.UUIDField(source="product.id")

    class Meta:
        model = CartItem
        fields = ["product_id"]


class CartProductQuantity(serializers.Serializer):
    product_id = serializers.UUIDField()
    quantity = serializers.IntegerField(default=1)

    def validate_quantity(self, value):
        """
        Validate that the quantity does not exceed 10.
        """
        if value > 10:
            raise serializers.ValidationError(
                "You can add a maximum of 10 products at a time."
            )
        return value
