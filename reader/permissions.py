from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrIfAuthentificatedReadOnly(BasePermission):
    """
    The request is authenticated as an admin user,  or is a read-only for non admin users.
    """

    def has_permission(self, request, view):
        return bool(
            (
                request.method in SAFE_METHODS
                and request.user
                and request.user.is_authenticated
            )
            or (request.user and request.user.is_staff)
        )


class IsOwnerOrReadOnly(BasePermission):
    """
    Custom permission to only allow owners of an object to view/edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Allow anyone to view (GET) their own profile.
        if request.method in SAFE_METHODS and obj == request.user.profile:
            return True

        # Allow only the owner to edit their own profile.
        return obj == request.user.profile


