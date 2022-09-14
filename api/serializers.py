from rest_framework import serializers
from tracker.models import Teams, Bug, MediaStore, Messeges, BugResolution

from django.contrib.auth import get_user_model
User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ('pk', 'username', 'email', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

class TeamsSerializer(serializers.ModelSerializer):
    team_leader_name = serializers.ReadOnlyField(source='team_leader.username')
    class Meta:
        model = Teams
        fields = ('pk', 'team_name', 'team_leader','team_leader_name')
        # depth = 0

class MediaStoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaStore
        fields = ('pk', 'media_file', 'media_type')

class BugsSerializer(serializers.ModelSerializer):
    found_by_username = serializers.ReadOnlyField(source='found_by.username')
    team_name = serializers.ReadOnlyField(source='team.team_name')
    attachment_list = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Bug
        fields = ('pk', 'title','description','reproduction_steps','found_by','found_by_username','acceptance','team', 'team_name','attachments','attachment_list')
        extra_kwargs = {'attachments': {'write_only': True}}


    def get_attachment_list(self, obj):
        attachments = obj.attachments.all().filter(deleted_at__isnull=True)
        return MediaStoreSerializer(attachments, many=True).data

class MessegesSerializer(serializers.ModelSerializer):
    attachment_list = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Messeges
        fields = ('pk', 'message', 'user', 'attachments', 'attachment_list')
        extra_kwargs = {'attachments': {'write_only': True}}

    
    def get_attachment_list(self, obj):
        attachments = obj.attachments.all().filter(deleted_at__isnull=True)
        return MediaStoreSerializer(attachments, many=True).data


class BugResolutionSerializer(serializers.ModelSerializer):
    messages_list = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = BugResolution
        fields = ('pk', 'bug', 'assigned_members', 'assigned_remarks','root_cause', 'error_function', 'error_function_owner', 'pull_req_id', 'merge_req_id', 'approved_by', 'end_time', 'messages_list')
        extra_kwargs = {'comments': {'write_only': True}}

    def get_messages_list(self, obj):
        attachments = Messeges.objects.all().filter(bug_resolution_id=obj).filter(deleted_at__isnull=True)
        return MessegesSerializer(attachments, many=True).data

