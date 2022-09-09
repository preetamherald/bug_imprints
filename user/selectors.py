from .models import User


def get_user_instance(user_id):
    qs = User.objects.get(id=user_id)
    if qs is not None:
        if qs.deleted_at is None:
            return qs
    return None

def get_user_teams(user_id):
    user = User.objects.get(id=user_id)
    teams =  getattr(user,"get_active_teams_list") 
    return teams

