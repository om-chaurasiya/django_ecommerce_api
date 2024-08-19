from django.contrib import admin

from shop.models import Cart, CartItem, Invoice, InvoiceItem, Product, User


class UserAdmin(admin.ModelAdmin):
    list_display = ("first_name", "email", "phone_number", "created_on")
    search_fields = (
        "first_name",
        "phone_number",
        "id",
        "email",
    )


admin.site.register(User, UserAdmin)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Invoice)
admin.site.register(Product)
admin.site.register(InvoiceItem)
