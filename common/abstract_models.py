from django.utils import timezone
from django.db import models
from common.middlewares import get_request
from django.contrib.auth import get_user_model
User = get_user_model()


# ABSTRACT BASE MODELS BLOCK #

class BaseModel(models.Model):
    '''
    This model shall be inherited,
    To add the functionality of maintaining the user who created and modified the object, 
    '''
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, related_name='%(class)s_created', on_delete=models.RESTRICT, null=False, blank=True)
    modified_by = models.ForeignKey(User, related_name='%(class)s_modified', on_delete=models.RESTRICT, null=False, blank=True)

    class Meta:
        abstract = True

    def save(self, auth_user = None, *args, **kwargs):
        '''
        set the created_by and modified_by to the user who is creating the object.
        and keeps updating the modified_by to the user who is modifying the object with the current time.

        if the method is called via request, the user will be fetched from the request object, no need to pass the user_id.
        if the method is called via shell, then the "auth_user=user_id" should be passed to the function.
        '''
        if auth_user is not None:
            # CASE: if user is passes as arguement, assign it
            self.modified_by = auth_user
        else:
            req = get_request()
            if req is None:
                # CASE: Request is unavailable and auth_user is not passed
                # Inference: The method is called via shell, so auth_user is required
                # Solution: Raise an error
                # Alternative: TODO: Check if we can send a login request in shell 
                return ValueError("kindly provide auth_user")                                                     
            # CASE: Request is available, so get the user from the request
            auth_user = getattr(req, 'user', None)
            if auth_user.is_anonymous is True:
                # CASE: user is not logged in
                # Solution: Raise an error
                # Remark: This block running indicates some APIs are not protected
                raise ValueError("Please login and try again")
        
        if self._state.adding:
            # CASE: if new object, set both created_by and modified_by to auth_user
            self.created_by = auth_user
            self.modified_by = auth_user
        else:
            # CASE: if existing object, only update the modified_by
            self.modified_by = auth_user
        return super(User,self).save(*args, **kwargs)

class SoftDeleteModel(models.Model):
    '''
    This model shall be inherited.
    To add the functionality of maintaining the user who deleted the object and allowing soft delete,
    '''
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(User, related_name='%(class)s_deleted', on_delete=models.RESTRICT, null=True, blank=True)

    class Meta:
        abstract = True

    def soft_delete(self, auth_user = None, *args, **kwargs): 
        '''
        set the deleted_by to the user who is deleting the object and set the deleted_at to the current time.

        if the method is called via request, the user will be fetched from the request object, no need to pass the user_id.
        if the method is called via shell, then the "auth_user=user_id" should be passed to the function.
        '''
        if auth_user is not None:
            # CASE: if user is passes as arguement, assign it
            self.deleted_by = auth_user
            self.modified_by = auth_user
        else:
            req = get_request()
            if req is not None:
                # CASE: Request is unavailable and auth_user is not passed
                # Inference: The method is called via shell, so auth_user is required
                # Solution: Raise an error
                # Alternative: TODO: Check if we can send a login request in shell 
                return ValueError("kindly provide auth_user") 
            auth_user = getattr(req, 'user', None)
            if auth_user.is_anonymous is True:
                # CASE: user is not logged in
                # Solution: Raise an error
                # Remark: This block running indicates some APIs are not protected
                raise ValueError("Please login and try again")
        self.deleted_by = auth_user
        self.modified_by = auth_user                            
        self.deleted_at = timezone.now()
        return self.save(auth_user=auth_user, *args, **kwargs)

    # def get_queryset(self):   
    #     # TODO: figure out how to fix this 
    #     return super(SoftDeleteModel, self).get_queryset().filter(deleted_at__isnull=True) 

# -------------------------------------------------------------------------------------------- #
