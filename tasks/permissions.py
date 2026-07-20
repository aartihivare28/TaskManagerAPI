from rest_framework.permissions import BasePermission


class IsOwnerOrReadOnly(BasePermission):
    """
    Only the owner of a task can update or delete it.
    Read access is allowed fo authenticated users.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return True
        
        return obj.owner == request.user
    