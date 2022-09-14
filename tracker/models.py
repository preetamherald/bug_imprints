from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()
from common.abstract_models import BaseModel, SoftDeleteModel


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