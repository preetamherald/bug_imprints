from rest_framework import status, serializers
from rest_framework.response import Response

from rest_framework import generics
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from rest_framework_simplejwt.authentication import JWTAuthentication

from tracker.services import add_messege_to_bug_resolution, upload_media_return_id
from tracker.selectors import get_assigned_team_members, get_team_members, get_team_leader

from .serializers import TeamsSerializer, BugsSerializer, BugResolutionSerializer
from tracker.models import Teams, Bug, Messeges, BugResolution

from .mixins import SoftDeleteModelMixin

from django.contrib.auth import get_user_model
User = get_user_model()


class TeamsList(generics.ListCreateAPIView):
    '''
    API View to add a new team or get all teams list
    Available to: admin (for adding new teams: POST), authenticated users (for getting all teams: GET)
    Method: GET, POST
    '''
    queryset = Teams.objects.all().filter(deleted_at__isnull=True)
    serializer_class = TeamsSerializer
    authentication_classes = [JWTAuthentication]
    
    def get_permissions(self):
        if self.request.method == 'GET':
            self.permission_classes = [IsAuthenticated]
        else:
            # CASE: POST, only admin can add new teams
            self.permission_classes = [IsAdminUser]
        return super(TeamsList, self).get_permissions()

    def get(self, request, *args, **kwargs):
        self.queryset = Teams.objects.select_related('team_leader').filter(deleted_at__isnull=True)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        '''This was just to see id i could check it this way. I can, but i do now wish to remove it now.'''
        if request.data.get('team_name') == "Preetam Hate Group":
            return Response({"error": "Noone say bad bad about preetam ;)"}, status=status.HTTP_400_BAD_REQUEST)
        return super().post(request, *args, **kwargs)

class TeamsDetail(SoftDeleteModelMixin, generics.RetrieveUpdateDestroyAPIView):
    '''
    API View to get detials of a team, update a team or delete a team
    Available to: Superuser (for all teams), Team leader (for their team), file owner or superuser (for DELETE operation) 
    Method: GET, PUT, PATCH, DELETE
    '''
    queryset = Teams.objects.all().filter(deleted_at__isnull=True)
    serializer_class = TeamsSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_permissions(self):
        if self.request.method == 'GET':
            self.permission_classes = [IsAuthenticated]
        else:
            # CASE: POST, PUT, PATCH, DELETE, 
            # only admin or team leader can update or delete a team
            # TODO: add team leader permission
            self.permission_classes = [IsAuthenticated] 
        return super(TeamsList, self).get_permissions()

class BugList(generics.ListCreateAPIView):
    '''
    API View to add a new Bug entry or get all bugs list
    Available to: admin (for adding new teams: POST), authenticated users (for getting all teams: GET)
    Method: GET, POST
    Available to: authenticated users
    '''
    queryset = Bug.objects.all().filter(deleted_at__isnull=True)
    serializer_class = BugsSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if request.data.get('acceptance') in [True, False]:
            return Response({"error": "Bug entry needs to be created first before updating acceptance"},
             status=status.HTTP_400_BAD_REQUEST)
        return super().post(request, *args, **kwargs)

    # def get_queryset(self): TODO: find ways to reduce queries
    #     user = self.request.user
    #     return Bug.objects.filter(Q(found_by=user) | Q(team__team_members=user)).filter(deleted_at__isnull=True)


class BugDetail(SoftDeleteModelMixin, generics.RetrieveUpdateDestroyAPIView):
    '''
    API View to get detials of a bug, update a bug or delete a bug
    Available to: Authenticated user, file owner or superuser (for DELETE operation) 
    Method: GET, PUT, PATCH, DELETE
    '''
    queryset = Bug.objects.all().filter(deleted_at__isnull=True)
    serializer_class = BugsSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'


class BugResolutionList(generics.ListCreateAPIView):
    '''
    API View to add a new Bug resolution entry or get all bugs resolutions list
    Available to: Team Leader (for adding new BugResolution: POST), Team Members (for getting all BugResolution list of team: GET)
    Method: GET, POST
    Available to: authenticated users
    '''
    queryset = BugResolution.objects.all().filter(deleted_at__isnull=True)
    serializer_class = BugResolutionSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs): 
        # CASE: only return bug resolutions available to the user
        self.queryset =  self.queryset.filter(bug__team__team_members=request.user).order_by('-created_at')
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class BugResolutionDetail(SoftDeleteModelMixin, generics.RetrieveUpdateDestroyAPIView):
    '''
    API View to get detials of a BugResolution, update a BugResolution or delete a BugResolution
    Available to: GET (Team Members), PUT/PATCH (assigned Team Members), DELETE (superuser or team leader)
    '''
    queryset = BugResolution.objects.all().filter(deleted_at__isnull=True)
    serializer_class = BugResolutionSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get(self, request, *args, **kwargs):
        team_id = self.get_object().bug.team.id
        # TODO: Instead of this way, check in get_permissions
        # CHECK: if user is a team member of the team
        if request.user not in get_team_members(team_id):
            return Response({"error": "You are not a member of this team"}, status=status.HTTP_400_BAD_REQUEST)
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        team_id = self.get_object().bug.team.id
        # TODO: Instead of this way, check in get_permissions
        # CHECK: if user is a assigned to the bugResolution 
        if request.user not in get_assigned_team_members(team_id):
            return Response({"error": "You are not a member of this team"}, status=status.HTTP_400_BAD_REQUEST)
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        team_id = self.get_object().bug.team.id
        # TODO: Instead of this way, check in get_permissions
        # CHECK: if user is a assigned to the bugResolution
        if request.user not in get_assigned_team_members(team_id):
            return Response({"error": "You are not a member of this team"}, status=status.HTTP_400_BAD_REQUEST)
        return self.partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        team_id = instance.bug.team.id
        # TODO: Instead of this way, check in get_permissions
        # CHECK: if user is a team leader of the team or superuser
        if (request.user == get_team_leader(team_id)) or (request.user.is_superuser):
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_403_FORBIDDEN)

    def perform_destroy(self, instance):
        instance.soft_delete() 
        return Response ({'message': 'Soft delete successful'}, status=status.HTTP_200_OK)



# ------------------------------------Updated format style---------------------------------#

class MessegeCreate(generics.CreateAPIView):
    '''
    API View to add a new Messege entry
    acccepts: message, attachments [], user_id, bug_resolution_id
    available to: authenticated users
    method: POST
    '''
    class MessegesSerializer(serializers.Serializer):
        message           = serializers.CharField(max_length=500, required=True)
        attachments       = serializers.FileField(required=False)
        user_id           = serializers.IntegerField(required=True)
        bug_resolution_id = serializers.IntegerField(required=True)

    queryset = Messeges.objects.all().filter(deleted_at__isnull=True)
    serializer_class = MessegesSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        context = add_messege_to_bug_resolution(**serializer.validated_data, 
            files = request.FILES.getlist("attachments"))

        return Response(context, status = status.HTTP_201_CREATED)


class MessegeDestroy(SoftDeleteModelMixin, generics.DestroyAPIView):
    '''
    API View to soft delete a new Messege entry
    acccepts: id
    available to: file owner, superuser
    method: DELETE
    '''
    queryset = Messeges.objects.all().filter(deleted_at__isnull=True)
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'


class TeamBugResolutionList(generics.RetrieveAPIView): # get all bug resolution entries for a team
    '''
    API View to get all bug resolution entries for a team
    acccepts: team_id
    available to: team members
    method: GET
    '''
    class TeamBugResolutionSerializer(serializers.ModelSerializer):
        team_leader_name = serializers.ReadOnlyField(source='team_leader.username')
        bug_resolution_list = serializers.SerializerMethodField(read_only=True)

        class Meta:
            model = Teams
            fields = ('pk', 'team_name', 'team_leader','team_leader_name','bug_resolution_list')


        def get_bug_resolution_list(self, obj):
            team_id = hasattr(obj, 'id')
            bug_resolution_list = BugResolution.objects.filter(bug__team__id=team_id).filter(deleted_at__isnull=True).order_by('-created_at')
            return BugResolutionSerializer(bug_resolution_list, many=True).data


    queryset = Teams.objects.all().filter(deleted_at__isnull=True)
    serializer_class = TeamBugResolutionSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get(self, request, *args, **kwargs):
        team_id = self.get_object().id
        if request.user not in get_team_members(team_id):
            return Response({"error": "You are not a member of this team"}, status=status.HTTP_400_BAD_REQUEST)
        return self.retrieve(request, *args, **kwargs)


class MediaUpload(generics.CreateAPIView):
    '''
    API View to upload media files
    acccepts: file []
    available to: authenticated users
    method: POST
    '''
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        files = request.FILES.getlist("attachment")
        if files is None or files == '' or files is []:
            return Response({'response': 'ERROR: No Files Received'}, status=status.HTTP_400_BAD_REQUEST)
        context = upload_media_return_id(files=files)
    
        return Response(context, status = status.HTTP_201_CREATED)

