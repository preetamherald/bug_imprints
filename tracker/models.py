from django.utils import timezone
from django.db import models
from tracker.middlewares import get_request

#from django.contrib.auth.models import User # Replaced with custom user
from django.contrib.auth import get_user_model
User = get_user_model()



# Start base model Block #

# this model shall be inherited by every model in this app.
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, related_name='%(class)s_created', on_delete=models.RESTRICT, null=False, blank=True)
    modified_by = models.ForeignKey(User, related_name='%(class)s_modified', on_delete=models.RESTRICT, null=False, blank=True)

    class Meta:
        abstract = True

    def save(self, auth_user = None, *args, **kwargs): # if calling via shell, user_id should be passed to the function.
        if auth_user is not None:
            self.modified_by = auth_user
        else:
            req = get_request()
            if req is not None:
                return ValueError("kindly provide auth_user")   # This case is possibe in case of shell use, ask user to provide required field, alternatively can give a cmd form to login in shell                                                   
            auth_user = getattr(req, 'user', None)
            if auth_user.is_anonymous is True:                               # this case can happed incase a not logged in user requests for deletion using any bug
                raise ValueError("Please login and try again")
        
        if self._state.adding:                                  # if new object, set both created_by and modified_by to auth_user
            self.created_by = auth_user
            self.modified_by = auth_user
        else:                                                   # if existing object, only update the modified_by
            self.modified_by = auth_user
        return super(User,self).save(*args, **kwargs)

# This model shall be inherited by every model that needs soft delete functionality.
class SoftDeleteModel(models.Model):
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(User, related_name='%(class)s_deleted', on_delete=models.RESTRICT, null=True, blank=True)

    class Meta:
        abstract = True

    def soft_delete(self, auth_user = None, *args, **kwargs):   # if calling via shell, user_id should be passed to the function.
        if auth_user is not None:                               # if user is passes as arguement, assign it
            self.deleted_by = auth_user
            self.modified_by = auth_user
        else:
            req = get_request()
            if req is not None:
                return ValueError("kindly provide auth_user")   # This case is possibe in case of shell use, ask user to provide required field, alternatively can give a cmd form to login in shell                                                   
            auth_user = getattr(req, 'user', None)
            if auth_user.is_anonymous is True:                               # this case can happed incase a not logged in user requests for deletion using any bug
                raise ValueError("Please login and try again")
        self.deleted_by = auth_user
        self.modified_by = auth_user                            # if user is not available in request, then it is a shell call, do not update deleted_by and modified_by
        self.deleted_at = timezone.now()                        # set deleted_at to current time
        return self.save(auth_user=auth_user, *args, **kwargs)  # save the model

    # def get_queryset(self):                                                                       #TODO figure out how to fix this 
    #     return super(SoftDeleteModel, self).get_queryset().filter(deleted_at__isnull=True) 

# End Base Model Block #

# -------------------------------------------------------------------------------------------- #

# Start Supporting Models Block #

class Teams(BaseModel, SoftDeleteModel):
    team_name = models.CharField(max_length=100, unique=True)
    team_leader = models.ForeignKey(User, related_name='%(class)s_team_leader', on_delete=models.RESTRICT, null=False)
    # team_members = models.ManyToManyField(User, related_name='%(class)s_team_members', blank=True)
    def __str__(self):
        return self.team_name + " - " + self.team_leader.username


# model to accept media files like images, videos, pdfs etc.
class MediaStore(BaseModel, SoftDeleteModel):
    media_file = models.FileField(upload_to='attachments/')
    media_type = models.CharField(max_length=20, default='etc')
    #media_owner is from created by field in BaseModel
    def __str__(self):
        return self.media_file.name + " - " + self.media_type


class Messeges(BaseModel, SoftDeleteModel):
    message = models.TextField()
    # comment_date = models.DateTimeField(auto_now_add=True) ## Removed, redundent since we can take from created_at field
    user = models.ForeignKey(User, related_name='%(class)s_user', on_delete=models.RESTRICT, null=True)
    attachments = models.ManyToManyField(MediaStore, related_name='%(class)s_attachments', blank=True)
    # attachments = GenericRelation(MediaStore, on_delete=models.RESTRICT, null=True, blank=True) ## Not worth it, DRF does not support Generic Relation serialization, implemented it with a complex method but removing it for simplicity sake.
    bug_resolution_id = models.ForeignKey('BugResolution', related_name='%(class)s_bug_resolution', on_delete=models.RESTRICT, null=False, blank=False)

    def __str__(self):
        return self.user.username + " - " + self.message

# End Supporting Models Block #

# -------------------------------------------------------------------------------------------- #

# Start Bug Tracker Block #

class Bug(BaseModel, SoftDeleteModel):
    title = models.CharField(max_length=100, null=False, blank=False)
    description = models.TextField(null=True, blank=True)
    reproduction_steps = models.TextField(null=True, blank=True)
    found_by = models.ForeignKey(User, related_name='%(class)s_found_by', on_delete=models.RESTRICT, null=True, blank=True)
    acceptance = models.BooleanField(default=None, null=True,blank=True, choices=[(True,'Aceepted'),(False,'Rejected'),(None,'Under Review')])
    team = models.ForeignKey(Teams, related_name='%(class)s_team', on_delete=models.RESTRICT, null=True, blank=True)
    attachments = models.ManyToManyField(MediaStore, related_name='%(class)s_attachments', blank=True)
    #attachments = GenericRelation(MediaStore, on_delete=models.RESTRICT, null=True, blank=True) ## Not worth it, DRF does not support Generic Relation serialization, implemented it with a complex method but removing it for simplicity sake.

    def __str__(self):
        if (self.acceptance == None):
            return self.title + " - Under Review"
        if (self.acceptance == True):
            return self.title + " - Accepted"
        return self.title + " - Rejected"


class BugResolution(BaseModel, SoftDeleteModel): 
    # Bug and Bug Resolution are sepetrated to prevent sparse matrix problem.
    bug = models.OneToOneField(Bug, related_name='%(class)s_bug', on_delete=models.RESTRICT, null=False, blank=False)
    assigned_members = models.ManyToManyField(User, related_name='%(class)s_assigned_members', blank=False)
    assigned_remarks = models.TextField(null=True, blank=True)
    # -------------------------------------------------------------------------------------------- #
    root_cause = models.TextField(null=True, blank=True)
    error_function = models.TextField(null=True, blank=True)
    error_function_owner = models.ForeignKey(User, related_name='%(class)s_error_function_owner', on_delete=models.RESTRICT, null=True, blank=True)
    pull_req_id = models.CharField(max_length=100, null=True, blank=True)
    #comments = models.ManyToManyField(Messeges, related_name='%(class)s_comments', blank=True)
    # -------------------------------------------------------------------------------------------- #
    merge_req_id = models.CharField(max_length=100, null=True, blank=True)
    approved_by = models.ForeignKey(User, related_name='%(class)s_approved_by', on_delete=models.RESTRICT, null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.bug.title

    def save(self, user_id=None, *args, **kwargs):
        if hasattr(self,"bug") and self.bug.acceptance == False:
            raise ValueError("Bug is rejected, cannot resolve it.")
        if hasattr(self,"bug") and self.bug is not None:
            self.bug.acceptance = True
            self.bug.save()
            return super().save(user_id, *args, **kwargs)
        return '{"error": "bug is None, Kindly provide a bug"}'



class BugWatch(BaseModel, SoftDeleteModel):
    bug = models.ForeignKey(Bug, related_name='%(class)s_bug', on_delete=models.RESTRICT, null=False)
    watcher = models.ForeignKey(User, related_name='%(class)s_watcher', on_delete=models.RESTRICT, null=False)

    def __str__(self):
        return str(self.id) + " - " + self.bug.title + " - " + self.watcher.username


class BugDuplicate(BaseModel, SoftDeleteModel):
    parent = models.ForeignKey(Bug, related_name='%(class)s_parent', on_delete=models.RESTRICT, null=False)
    child = models.ForeignKey(Bug, related_name='%(class)s_child', on_delete=models.RESTRICT, null=False)

    def __str__(self):
        return str(self.id) + " - " + self.parent.title + " - " + self.child.title

# End Bug Tracker Block #