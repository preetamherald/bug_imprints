# from rest_framework.permissions import BasePermission, SAFE_METHODS


# class IsTeamLead(BasePermission):
#     """
#     Allows access only to authenticated users.
#     """

#     def has_permission(self, request, view):
#         return bool(request.user and (request.user.is_superuser or request.user in request.team.team_leads.all() ))


                
#         # print(request.data.get('bug_resolution_id'))
#         # print(request.data.get('user_id'))
#         # print(request.data.get('message'))
#         # print(request.data.get('attachments'))
#         # print(request.data.get('file_type'))
#         # # print(request.FILES['attachments'])
#         # print(request.FILES.getlist("attachments"))
#         # print((request.FILES.getlist("attachments") == []))