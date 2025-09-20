from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.response import Response
from rest_framework import status
from functools import wraps



class Role:

    ADMIN = 0

    DEVELOPER = 1

    ENTERPRISE = 2


ROLE_CHOICES = [

    (Role.ADMIN, 'Admin'),

    (Role.DEVELOPER, 'Developer'),

    (Role.ENTERPRISE, 'Enterprise')

]


def has_permission(request):
    return bool(
        request.method in SAFE_METHODS or
        request.user and
        request.user.is_authenticated
    )

def allowed_roles(roles):
    def decorator(action):
        @wraps(action)
        def wrapper(self, request, *args, **kwargs):
            user = request.user
            print("allowed:", request.user)
            if not user.is_authenticated:
                return Response({'detail': 'Authentication credentials were not provided.'}, status=status.HTTP_401_UNAUTHORIZED)
            profile = getattr(user, 'profile', None)
            if profile and profile.role not in roles:
                return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
            return action(self, request, *args, **kwargs)
        return wrapper
    return decorator

