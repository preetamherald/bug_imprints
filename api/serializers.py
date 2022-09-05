from msilib.schema import Media
from django.contrib.auth.models import User
from rest_framework import serializers
from tracker.models import Teams, Bug, MediaStore, Messeges, BugResolution, BugWatch, BugDuplicate


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('pk', 'username')

class TeamsSerializer(serializers.HyperlinkedModelSerializer):
    team_leader = UserSerializer(many=False, read_only=False)
    class Meta:
        model = Teams
        fields = ('pk', 'team_name', 'team_leader')

class MediaStoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaStore
        fields = ('pk', 'media_file', 'media_type')

class MessegesSerializer(serializers.ModelSerializer):
    attachments = MediaStoreSerializer(many=True, read_only=False)
    class Meta:
        model = Messeges
        fields = ('pk', 'message', 'comment_date', 'user', 'attachments')

class BugSerializer(serializers.HyperlinkedModelSerializer):
    found_by = UserSerializer(many=False, read_only=False)
    team = TeamsSerializer(many=False, read_only=False)
    media = MediaStoreSerializer(many=True, read_only=False)
    accept_status = serializers.SerializerMethodField(read_only = False)

    class Meta:
        model = Bug
        fields = ('pk', 'title','description','reproduction_steps','found_by','accept_status','team','media')

    def get_accept_status(self, obj):
        if obj.acceptance is None:
            return "Under Review"
        if obj.acceptance is True:
            return "Accepted"
        return "Rejected"

class BugResolutionSerializer(serializers.ModelSerializer):
    comments = MessegesSerializer(many=True, read_only=False)
    bug = BugSerializer(many=False, read_only=False)
    assigned_members = UserSerializer(many=True, read_only=False)
    approved_by = UserSerializer(many=False, read_only=False)

    class Meta:
        model = BugResolution
        fields = ('pk', 'bug','assigned_members', 'assigned_remarks', 'pull_req_id', 'comments', 'merge_req_id', 'approved_by', 'end_time')

class BugWatchSerializer(serializers.ModelSerializer):
    bug = BugSerializer(many=False, read_only=False)
    watcher = UserSerializer(many=False, read_only=False)
    class Meta:
        model = BugWatch
        fields = ('pk', 'bug','watcher')

class BugDuplicateSerializer(serializers.ModelSerializer):
    parent = BugSerializer(many=False, read_only=False)
    child = BugSerializer(many=False, read_only=False)
    class Meta:
        model = BugDuplicate
        fields = ('pk', 'parent','child')


    

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