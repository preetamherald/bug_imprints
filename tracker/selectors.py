from xml.dom import ValidationErr
from .models import Teams, BugResolution
from user.models import User

from user.selectors import get_user_instance

# get_team_leader = lambda team_id: Teams.objects.get(id=team_id).team_leader

def get_team_leader(team_id):
    qs = Teams.objects.get(deleted_at = None,id=team_id)
    return qs.team_leader

def get_team_instance(team_id):
    qs = Teams.objects.get(deleted_at = None,id=team_id)
    return qs

def get_bug_resolution_instance(bug_resolution_id):
    qs = BugResolution.objects.get(deleted_at = None,id=bug_resolution_id)
    return qs

def get_team_members(team_id):
    team  = get_team_instance(team_id)
    qs = User.objects.all().filter(deleted_at = None, teams__in=[team])
    return qs

def get_assigned_bug_resolutions(user_id):
    user = get_user_instance(user_id)
    qs = BugResolution.objects.filter(deleted_at = None, assigned_members__in = [user])
    return qs

def get_assigned_team_members(bug_resolution_id):
    bug_resolution = get_bug_resolution_instance(bug_resolution_id)
    return bug_resolution.assigned_members.all().filter(deleted_at = None)
