from .models import User


def get_user_instance(user_id):
    '''
    This function returns the user instance if the user exists or if it's not soft deleted,
    else it returns None
    '''
    user = User.objects.get(id=user_id)
    if user is not None:
        if user.deleted_at is None:
            return user
    return None

def get_user_teams(user_id):
    '''
    Returns queryset of Teams of the provided user: Teams model.
    '''
    user = User.objects.get(id=user_id)
    teams =  getattr(user,"get_active_teams_list") 
    return teams

