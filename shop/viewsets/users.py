from typing import Any

from django.contrib.auth import authenticate, login, logout
from rest_framework import status, viewsets
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from shop.models import User
from shop.serializers import (
    UserLoginSerializer,
    UserRegisterSerializer,
    UserUpdateSerializer,
)
from shop.utils import is_authenticate


class UserViewSet(
    viewsets.GenericViewSet,
):
    """API view set for User model."""

    queryset = User.objects.all()
    serializer_class = UserLoginSerializer

    @action(
        methods=["post"],
        detail=False,
        name="login",
    )
    def login(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            request=request,
            username=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )
        if user is not None:
            login(request, user)
            response = Response(
                status=status.HTTP_200_OK, data={"details": "Successfully Login"}
            )
            return response

        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"details": "You have enter wrong details"},
        )

    @action(
        methods=["post"],
        detail=False,
        name="register",
        serializer_class=UserRegisterSerializer,
    )
    def register(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        if is_authenticate(request):
            return Response(
                {
                    "detail": "First logged out the current account then Try to Register."
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if (
            serializer.validated_data["password"]
            != serializer.validated_data["password_again"]
        ):
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"details": "Password Mismatch"},
            )
        try:
            User.objects.get(email=serializer.validated_data["email"])
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={
                    "details": "Active Account with this email already exist, Please choose another email"
                },
            )
        except User.DoesNotExist:
            User.objects.create_user(
                email=serializer.validated_data["email"],
                password=serializer.validated_data["password"],
                first_name=serializer.validated_data["first_name"],
                last_name=serializer.validated_data["last_name"],
            )
        return Response(
            status=status.HTTP_201_CREATED,
            data={"details": "Account Created successfully,Please login"},
        )

    @action(
        methods=["get"],
        detail=False,
        name="logout",
    )
    @permission_classes([IsAuthenticated])
    def logout(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        if bool(request.user and request.user.is_authenticated):
            logout(request)
            return Response(
                status=status.HTTP_200_OK,
                data={"details": "Logout Successfully"},
            )
        else:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"details": "User logged out already"},
            )

    @action(
        methods=["delete"],
        detail=False,
        name="delete",
    )
    @permission_classes([IsAuthenticated])
    def delete(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        if not is_authenticate(request):
            return Response(
                {
                    "detail": "Authentication credentials were not provided OR May be deleted User."
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )
        request.user.delete()
        logout(request)
        return Response(
            status=status.HTTP_204_NO_CONTENT,
            data={"details": "User deleted Successfully"},
        )

    @action(
        methods=["patch"],
        detail=False,
        name="update",
        serializer_class=UserUpdateSerializer,
    )
    @permission_classes([IsAuthenticated])
    def update_user(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        if not is_authenticate(request):
            return Response(
                {
                    "detail": "Authentication credentials were not provided OR May be deleted User."
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )
        user = request.user
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            status=status.HTTP_200_OK,
            data={"details": "User updated successfully"},
        )
