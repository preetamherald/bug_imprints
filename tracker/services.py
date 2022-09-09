#services
from . selectors import get_bug_resolution_instance, get_team_members
from user.selectors import get_user_instance
from . models import Messeges, MediaStore, BugResolution

from user.models import User


def add_messege_to_bug_resolution(message, attachments, user_id, bug_resolution_id, auth_user: User = None, files = []):
    if message is None or user_id is None or bug_resolution_id is None:
        return {"error": "Invalid data"}
    
    bug_resolution = get_bug_resolution_instance(bug_resolution_id=bug_resolution_id)
    if bug_resolution is None:
        return ({'error': 'Bug resolution does not exist'})
    
    user = get_user_instance(user_id=user_id)
    if user is None:
        return ({'error': 'User does not exist'})

    if user not in get_team_members(team_id=bug_resolution.team.id):
        return ({'error': 'User is not a member of the team'})
    
    messege = Messeges.objects.create(message=message, user=user, bug_resolution_id=bug_resolution)
    messege.save(auth_user = auth_user)
    
    file_response = _add_files_to_obj(messege, files, auth_user)
    
    return ({"response": "Messege Successfully added to bug resolution", "files": file_response})


def _add_files_to_obj(obj, files, auth_user: User = None):
    
    if obj is None:
        return {"status": "Error : Invalid data"}

    if files is []:
        return {"status": "No Files to add"}
        
    for file in files:
        media_store = MediaStore.objects.create(media_file=file, media_type=file.content_type)
        media_store.save(auth_user = auth_user)
        obj.attachments.add(media_store)

    return ({"response": "Files Successfully added to object"})

