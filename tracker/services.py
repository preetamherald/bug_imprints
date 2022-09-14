#services
from . selectors import get_bug_resolution_instance, get_team_members
from user.selectors import get_user_instance
from . models import Messeges, MediaStore

from user.models import User


def add_messege_to_bug_resolution(message, attachments, user_id, bug_resolution_id, auth_user: User = None, files = []):
    '''
    This function adds a messege to a bug resolution.
    '''
    # CHECK: Check if all input data is valid.
    if message is None or user_id is None or bug_resolution_id is None:
        return {"error": "Invalid data"}
    
    bug_resolution = get_bug_resolution_instance(bug_resolution_id=bug_resolution_id)
    # CEHCK: Check if bug resolution exists, and is not soft deleted.
    if bug_resolution is None:
        return ({'error': 'Bug resolution does not exist'})
    
    user = get_user_instance(user_id=user_id)
    # CHECK: Check if user exists, and is not soft deleted.
    if user is None:
        return ({'error': 'User does not exist'})

    # CHECK: Check if user is a member of the team.
    if user not in get_team_members(team_id=bug_resolution.team.id):
        return ({'error': 'User is not a member of the team'})
    
    messege = Messeges.objects.create(message=message, user=user, bug_resolution_id=bug_resolution)
    messege.save(auth_user = auth_user)
    
    file_response = "Not Files Provided"
    # CHECK: Check if files are provided.
    if files is not None and files != []:
        file_response = _add_files_to_obj(messege, files, auth_user)
    
    return ({"response": "Messege Successfully added to bug resolution", "files": file_response})

def upload_media_return_id(files, auth_user: User = None, *args, **kwargs):
    '''
    This function uploads media files to the media store, and returns ID of the media file.
    '''
    upload_status = []
    for file in files:
        media_store = MediaStore.objects.create(media_file=file, media_type=file.content_type)
        media_store.save(auth_user = auth_user)
        upload_status.append(media_store.id)

    return {'response': 'Upload Successful', 'id': upload_status}

def _add_files_to_obj(obj, files, auth_user: User = None):
    '''
    This function uploads media files to the media store and adds them to the provided object.
    '''
    # CHECK: Check if all input data is valid.
    if obj is None or files is None or files is []:
        return {"status": "Error : Invalid data"}

    # upload_status = []
    for file in files:
        # TODO: object retuns ID, needs instance of object, commented to work on later
        # upload_status.append(upload_media_return_id(file, auth_user)) 
        media_store = MediaStore.objects.create(media_file=file, media_type=file.content_type)
        media_store.save(auth_user = auth_user)
        obj.attachments.add(media_store)

    return ({"response": "Files Successfully added to object"})

