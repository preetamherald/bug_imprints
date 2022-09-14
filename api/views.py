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
    queryset = Teams.objects.all().filter(deleted_at__isnull=True)
    serializer_class = TeamsSerializer
    authentication_classes = [JWTAuthentication]
    
    def get_permissions(self):
        if self.request.method == 'GET':
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [IsAdminUser] # only admin can create teams
        return super(TeamsList, self).get_permissions()

    def get(self, request, *args, **kwargs):
        self.queryset = Teams.objects.select_related('team_leader').filter(deleted_at__isnull=True)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """This was just to see id i could check it this way. I can, but i do now wish to remove it now."""
        if request.data.get('team_name') == "Preetam Hate Group":
            return Response({"error": "Noone say bad bad about preetam ;)"}, status=status.HTTP_400_BAD_REQUEST)
        return super().post(request, *args, **kwargs)

class TeamsDetail(SoftDeleteModelMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Teams.objects.all().filter(deleted_at__isnull=True)
    serializer_class = TeamsSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

class BugList(generics.ListCreateAPIView):
    queryset = Bug.objects.all().filter(deleted_at__isnull=True)
    serializer_class = BugsSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if request.data.get('acceptance') in [True, False]:
            return Response({"error": "Bug entry needs to be created first before updating acceptance"}, status=status.HTTP_400_BAD_REQUEST)
        return super().post(request, *args, **kwargs)

    # def get_queryset(self): TODO: find ways to reduce queries
    #     user = self.request.user
    #     return Bug.objects.filter(Q(found_by=user) | Q(team__team_members=user)).filter(deleted_at__isnull=True)


class BugDetail(SoftDeleteModelMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Bug.objects.all().filter(deleted_at__isnull=True)
    serializer_class = BugsSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'


class BugResolutionList(generics.ListCreateAPIView):
    queryset = BugResolution.objects.all().filter(deleted_at__isnull=True)
    serializer_class = BugResolutionSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs): # only return bug resolutions available to the user
        self.queryset =  self.queryset.filter(bug__team__team_members=request.user).order_by('-created_at')
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class BugResolutionDetail(SoftDeleteModelMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = BugResolution.objects.all().filter(deleted_at__isnull=True)
    serializer_class = BugResolutionSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get(self, request, *args, **kwargs):
        team_id = self.get_object().bug.team.id
        if request.user not in get_team_members(team_id):
            return Response({"error": "You are not a member of this team"}, status=status.HTTP_400_BAD_REQUEST)
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        team_id = self.get_object().bug.team.id
        if request.user not in get_assigned_team_members(team_id):
            return Response({"error": "You are not a member of this team"}, status=status.HTTP_400_BAD_REQUEST)
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        team_id = self.get_object().bug.team.id
        if request.user not in get_assigned_team_members(team_id):
            return Response({"error": "You are not a member of this team"}, status=status.HTTP_400_BAD_REQUEST)
        return self.partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        team_id = instance.bug.team.id
        if (request.user == get_team_leader(team_id)) or (request.user.is_superuser): # only the teamLeader or superuser can soft delete
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_403_FORBIDDEN)

    def perform_destroy(self, instance):
        instance.soft_delete() 
        return Response ({'message': 'Soft delete successful'}, status=status.HTTP_200_OK)



# ------------------------------------Updated format style---------------------------------#

class MessegeCreate(generics.CreateAPIView):
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

        context = add_messege_to_bug_resolution(**serializer.validated_data, files = request.FILES.getlist("attachments"))

        return Response(context, status = status.HTTP_201_CREATED)


class MessegeDestroy(SoftDeleteModelMixin, generics.DestroyAPIView):
    queryset = Messeges.objects.all().filter(deleted_at__isnull=True)
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'


class TeamBugResolutionList(generics.RetrieveAPIView): # get all bug resolution entries for a team
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
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        files = request.FILES.getlist("attachment")
        if files is None or files == '' or files is []:
            return Response({'response': 'ERROR: No Files Received'}, status=status.HTTP_400_BAD_REQUEST)
        context = upload_media_return_id(files=files)
    
        return Response(context, status = status.HTTP_201_CREATED)

