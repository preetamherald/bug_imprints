from rest_framework import status
from rest_framework.response import Response

class SoftDeleteModelMixin:
    """
    Soft Delete a model instance.
    Available to: superuser, creator
    """
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # CHECK: if the user is superuser or the creator of the object
        if (request.user == instance.created_by) or (request.user.is_superuser):
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_403_FORBIDDEN)

    def perform_destroy(self, instance):
        instance.soft_delete() 
        return Response ({'message': 'Soft delete successful'}, status=status.HTTP_200_OK)