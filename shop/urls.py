from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter
from rest_framework.schemas import get_schema_view

from shop.viewsets import billing, cart, users

router = DefaultRouter()

urlpatterns = [
    path(
        "openapi/",
        get_schema_view(
            title="E-commerce API",
            description="All API's for E-commerce",
            version="1.0.0",
        ),
        name="openapi-schema",
    ),
    path(
        "",
        TemplateView.as_view(
            template_name="swagger-ui.html",
            extra_context={"schema_url": "openapi-schema"},
        ),
        name="swagger-ui",
    ),
]


router.register(r"profile", users.UserViewSet, basename="login")
router.register(r"cart", cart.CartViewSet, basename="cart")
router.register(r"invoice", billing.BillingViewSet, basename="billing")

urlpatterns += [
    path("", include(router.urls)),
]
