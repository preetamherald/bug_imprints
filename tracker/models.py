from django.utils import timezone
from django.db import models
from tracker.middlewares import get_request

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

# Supporting Models Block #

class Teams(BaseModel, SoftDeleteModel):
    '''
    Teams model maintains the record of the teams along with their leaders.
    '''
    team_name = models.CharField(max_length=100, unique=True)
    team_leader = models.ForeignKey(User, related_name='%(class)s_team_leader', on_delete=models.RESTRICT, null=False)
    # team_members = models.ManyToManyField(User, related_name='%(class)s_team_members', blank=True)
    def __str__(self):
        return self.team_name + " - " + self.team_leader.username


# model to accept media files like images, videos, pdfs etc.
class MediaStore(BaseModel, SoftDeleteModel):
    '''
    MediaStore is used to store all media being used in the application.
    '''
    media_file = models.FileField(upload_to='attachments/')
    media_type = models.CharField(max_length=20, default='etc')
    # media_owner is from created by field in BaseModel
    def __str__(self):
        return self.media_file.name + " - " + self.media_type


class Messeges(BaseModel, SoftDeleteModel):
    '''
    Messeges model maintains the record of the messeges (comments) by the users.
    '''
    message = models.TextField()
    user = models.ForeignKey(User, related_name='%(class)s_user', on_delete=models.RESTRICT, null=True)
    attachments = models.ManyToManyField(MediaStore, related_name='%(class)s_attachments', blank=True)
    bug_resolution_id = models.ForeignKey('BugResolution', related_name='%(class)s_bug_resolution', on_delete=models.RESTRICT, null=False, blank=False)

    def __str__(self):
        return self.user.username + " - " + self.message

# -------------------------------------------------------------------------------------------- #

# Bug Tracker Block #

class Bug(BaseModel, SoftDeleteModel):
    '''
    Bug model stores the initial submitted details of the bug, 
    The details added to this are subject to acceptance.
    Upon acceptance, the bug life cycle will be managed in BugResolution model.
    '''
    title = models.CharField(max_length=100, null=False, blank=False)
    description = models.TextField(null=True, blank=True)
    reproduction_steps = models.TextField(null=True, blank=True)
    found_by = models.ForeignKey(User, related_name='%(class)s_found_by', on_delete=models.RESTRICT, null=True, blank=True)
    acceptance = models.BooleanField(default=None, null=True,blank=True, choices=[(True,'Aceepted'),(False,'Rejected'),(None,'Under Review')])
    team = models.ForeignKey(Teams, related_name='%(class)s_team', on_delete=models.RESTRICT, null=True, blank=True)
    attachments = models.ManyToManyField(MediaStore, related_name='%(class)s_attachments', blank=True)

    def __str__(self):
        if (self.acceptance == None):
            return str(self.id) + self.title + " - Under Review"
        if (self.acceptance == True):
            return str(self.id) + self.title + " - Accepted"
        return str(self.id) + self.title + " - Rejected"

    # TODO: add a method to accept/reject the bug, 
    # and signal creation of BugResolution object on acceptance


class BugResolution(BaseModel, SoftDeleteModel): 
    '''
    BugResolution model is used to manage the life cycle of the bug after acceptance.
    Seperated from Bug model to avoid sparse matrix of fields.
    '''
    
    bug = models.OneToOneField(Bug, related_name='%(class)s_bug', on_delete=models.RESTRICT, null=False, blank=False)
    assigned_members = models.ManyToManyField(User, related_name='%(class)s_assigned_members', blank=False)
    assigned_remarks = models.TextField(null=True, blank=True)
    # -------------------------------------------------------------------------------------------- #
    root_cause = models.TextField(null=True, blank=True)
    error_function = models.TextField(null=True, blank=True)
    error_function_owner = models.ForeignKey(User, related_name='%(class)s_error_function_owner', on_delete=models.RESTRICT, null=True, blank=True)
    pull_req_id = models.CharField(max_length=100, null=True, blank=True)
    # -------------------------------------------------------------------------------------------- #
    merge_req_id = models.CharField(max_length=100, null=True, blank=True)
    approved_by = models.ForeignKey(User, related_name='%(class)s_approved_by', on_delete=models.RESTRICT, null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.bug.title

    def save(self, user_id=None, *args, **kwargs):
        if hasattr(self,"bug") and self.bug.acceptance == False:
            # CASE: Rejected bugs cannot be used to create BugResolution
            raise ValueError("Bug is rejected, cannot resolve it.")
        if hasattr(self,"bug") and self.bug is not None:
            # CASE: if the bug is not rejected, then accept the bug and create bug resolution object
            self.bug.acceptance = True
            self.bug.save()
            return super().save(user_id, *args, **kwargs)

        # CASE: if the bug is not provided, then return error and do nothing 
        return '{"error": "bug is None, Kindly provide a bug"}'



class BugWatch(BaseModel, SoftDeleteModel):
    '''
    BugWatch models stores the details of the users who are watching the bug.
    People who are watching the bug will be notified of any changes in the bug.
    '''
    bug = models.ForeignKey(Bug, related_name='%(class)s_bug', on_delete=models.RESTRICT, null=False)
    watcher = models.ForeignKey(User, related_name='%(class)s_watcher', on_delete=models.RESTRICT, null=False)

    def __str__(self):
        return str(self.id) + " - " + self.bug.title + " - " + self.watcher.username


class BugDuplicate(BaseModel, SoftDeleteModel):
    '''
    BugDuplicate models stores the details of the bugs which are duplicates 
    or the bugs that are resolved by resolving the parent bug.
    '''
    parent = models.ForeignKey(Bug, related_name='%(class)s_parent', on_delete=models.RESTRICT, null=False)
    child = models.ForeignKey(Bug, related_name='%(class)s_child', on_delete=models.RESTRICT, null=False)

    def __str__(self):
        return str(self.id) + " - " + self.parent.title + " - " + self.child.title

# -------------------------------------------------------------------------------------------- #