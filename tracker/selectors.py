from xml.dom import ValidationErr
from .models import Teams, BugResolution
from user.models import User

from user.selectors import get_user_instance

# get_team_leader = lambda team_id: Teams.objects.get(id=team_id).team_leader

# TODO: implement get_object_or_404 for the following functions 
# or a suitable alternative to return a 404 response in JSON format.

def get_team_instance(team_id):
    '''
    Returns an instance of the team: Teams model.
    '''
    qs = Teams.objects.get(deleted_at = None,id=team_id)
    return qs

def get_team_leader(team_id):
    '''
    Returns an instance of the team leader: User model.
    '''
    team_leader = get_team_instance(team_id).team_leader
    return team_leader

def get_bug_resolution_instance(bug_resolution_id):
    '''
    Returns an instance of the bug resolution: BugResolution model.
    '''
    bugResolution = BugResolution.objects.get(deleted_at = None,id=bug_resolution_id)
    return bugResolution

def get_team_members(team_id):
    '''
    Returns queryset of Team Members of the provided team: User model.
    '''
    team  = get_team_instance(team_id)
    qs = User.objects.all().filter(deleted_at = None, teams__in=[team])
    return qs

def get_assigned_bug_resolutions(user_id):
    '''
    Returns queryset of BugResolutions assgned to the user: BugResolution model.
    '''
    user = get_user_instance(user_id)
    qs = BugResolution.objects.filter(deleted_at = None, assigned_members__in = [user])
    return qs

def get_assigned_team_members(bug_resolution_id):
    '''
    Returns queryset of Team Members assigned to the bug resolution: User model.
    '''
    qs = get_bug_resolution_instance(bug_resolution_id)
    return qs.assigned_members.all().filter(deleted_at = None)
