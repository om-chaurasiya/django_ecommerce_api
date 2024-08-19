def is_authenticate(request):
    return bool(request.user and request.user.is_authenticated)
