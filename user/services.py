from tracker.selectors import get_team_leader, get_team_instance
from user.selectors import get_user_instance, get_user_teams

from .models import User


def add_team_to_user(user_id: int, team_id: int, auth_user: User ): #TODO change name to add_team_to_user
    if auth_user is None or user_id is None or team_id is None:
        return {"error": "Invalid data"}

    team = get_team_instance(team_id=team_id)
    if team is None:
        return ({'error': 'Team does not exist'})
    
    if auth_user.is_superuser is False:
        if auth_user != get_team_leader(team_id=team_id):
            return {"error": "You are not authorized to add team to user"}
 
    user = get_user_instance(user_id=user_id)
    if user is None:
        return ({'error': 'User does not exist'})

    if team in get_user_teams(user_id=user_id):
        return ({"response": "Team already exists"})

    user.teams.add(team)   
    user.clean() #TODO check if this is needed and find a way to do it without using this. 
    user.save(auth_user = auth_user) 
    return ({"response": "Team Successfully added to user"})

def remove_team_from_user(user_id: int, team_id: int, auth_user: User ):
    if auth_user is None or user_id is None or team_id is None:
        return {"error": "Invalid data"}

    team = get_team_instance(team_id=team_id)
    if team is None:
        return ({'error': 'Team does not exist'})
    
    if auth_user.is_superuser is False:
        if auth_user != get_team_leader(team_id=team_id):
            return {"error": "You are not authorized to add team to user"}
 
    user = get_user_instance(user_id=user_id)
    if user is None:
        return ({'error': 'User does not exist'})

    if team not in get_user_teams(user_id=user_id):
        return ({"response": "User not part of team"})
    
    user.teams.remove(team)   
    user.clean()
    user.save(auth_user = auth_user)
    return ({"response": "Team Successfully removed from user"})

def update_account_type(user_id: int, account_type: str, auth_user: User ):
    if auth_user is None or user_id is None or account_type is None:
        return {"error": "Invalid data"}

    if account_type not in ['W', 'C', 'T', 'S']:
        return {"error": "Invalid account type"}

    if auth_user.is_superuser is False:
        return {"error": "You are not authorized to update user account type"}
 
    user = get_user_instance(user_id=user_id)
    if user is None:
        return ({'error': 'User does not exist'})

    user.account_type = account_type
    user.clean()
    user.save(auth_user = auth_user)
    return ({"response": "Account type Successfully updated"})

def disable_account(user_id: int, auth_user: User ):
    if auth_user is None or user_id is None:
        return {"error": "Invalid data"}

    if auth_user.is_superuser is False:
        return {"error": "You are not authorized to disable user account"}
 
    user = get_user_instance(user_id=user_id)
    if user is None:
        return ({'error': 'User does not exist'})

    user.is_active = False
    user.soft_delete(auth_user = auth_user)
    user.clean()
    user.save(auth_user = auth_user)
    return ({"response": "Account Successfully disabled"})