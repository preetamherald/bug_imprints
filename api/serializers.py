from msilib.schema import Media
from os import defpath
from urllib import request
from rest_framework import serializers
from tracker.models import Teams, Bug, MediaStore, Messeges, BugResolution, BugWatch, BugDuplicate

#from django.contrib.auth.models import User # Replaced with custom user
from django.contrib.auth import get_user_model
User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ('pk', 'username', 'email', 'password')
        # extra_kwargs = {
        #     'password': {'write_only': True},
        # }

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
    # attachments = MediaStoreSerializer(many=True, read_only=True)
    # attachments = serializers.SerializerMethodField(read_only=True) ## used to add generic relation data, now removed
    attachment_list = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Bug
        fields = ('pk', 'title','description','reproduction_steps','found_by','found_by_username','acceptance','team', 'team_name','attachments','attachment_list')
        extra_kwargs = {'attachments': {'write_only': True}}


    def get_attachment_list(self, obj):
        attachments = obj.attachments.all().filter(deleted_at__isnull=True)
        return MediaStoreSerializer(attachments, many=True).data

    # def get_attachments(self, obj):  ## used to add generic relation data, now removed 
    #     attachments = obj.attachments.all().filter(deleted_at__isnull=True)
    #     return MediaStoreSerializer(attachments, many=True).data

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







# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ('pk', 'username')


# class MessegesSerializer(serializers.ModelSerializer):
#     attachments = MediaStoreSerializer(many=True, read_only=False)
#     class Meta:
#         model = Messeges
#         fields = ('pk', 'message', 'comment_date', 'user', 'attachments')

# class BugSerializer(serializers.HyperlinkedModelSerializer):
#     found_by = UserSerializer(many=False, read_only=False)
#     team = TeamsSerializer(many=False, read_only=False)
#     media = MediaStoreSerializer(many=True, read_only=False)
#     accept_status = serializers.SerializerMethodField(read_only = False)

#     class Meta:
#         model = Bug
#         fields = ('pk', 'title','description','reproduction_steps','found_by','accept_status','team','media')

#     def get_accept_status(self, obj):
#         if obj.acceptance is None:
#             return "Under Review"
#         if obj.acceptance is True:
#             return "Accepted"
#         return "Rejected"

# class BugResolutionSerializer(serializers.ModelSerializer):
#     comments = MessegesSerializer(many=True, read_only=False)
#     bug = BugSerializer(many=False, read_only=False)
#     assigned_members = UserSerializer(many=True, read_only=False)
#     approved_by = UserSerializer(many=False, read_only=False)

#     class Meta:
#         model = BugResolution
#         fields = ('pk', 'bug','assigned_members', 'assigned_remarks', 'pull_req_id', 'comments', 'merge_req_id', 'approved_by', 'end_time')

# class BugWatchSerializer(serializers.ModelSerializer):
#     bug = BugSerializer(many=False, read_only=False)
#     watcher = UserSerializer(many=False, read_only=False)
#     class Meta:
#         model = BugWatch
#         fields = ('pk', 'bug','watcher')

# class BugDuplicateSerializer(serializers.ModelSerializer):
#     parent = BugSerializer(many=False, read_only=False)
#     child = BugSerializer(many=False, read_only=False)
#     class Meta:
#         model = BugDuplicate
#         fields = ('pk', 'parent','child')


    

# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ('username', 'password',)
        
#         extra_kwargs = {'password': {'write_only': True}}

#     def create(self, validated_data):
#         password = validated_data.pop('password', None)
#         instance = self.Meta.model(**validated_data)
#         if password is not None:
#             instance.set_password(password)
#         instance.save()
#         return instance

#     def update(self, instance, validated_data):
#         for attr, value in validated_data.items():
#             if attr == 'password':
#                 instance.set_password(value)
#             else:
#                 setattr(instance, attr, value)
#         instance.save()
#         return instance