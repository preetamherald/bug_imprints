from django.shortcuts import render

from rest_framework.response import Response
from rest_framework import generics, status, serializers
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import User
from .services import add_user_to_team, remove_team_from_user, update_account_type, disable_account

# Create your views here.

class AddUserToTeam(generics.GenericAPIView):
    '''
    API View to add a user to a team
    Accepts: user_id, team_id
    Available to: Superuser (for all teams), Team leader (for their team)
    Method: POST
    '''
    class InputSerializer(serializers.Serializer):
        user_id = serializers.IntegerField(required=True)
        team_id = serializers.IntegerField(required=True)

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated] # removed IsAdminUser permission since team leaders can also add users to team
    serializer_class = InputSerializer

    def post(self, request , *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user_id = serializer.validated_data['user_id']
        team_id = serializer.validated_data['team_id']
        response = add_user_to_team(user_id=user_id, team_id=team_id, auth_user=request.user)
        return Response(response, status=status.HTTP_200_OK)

class RemoveUserFromTeam(generics.GenericAPIView):
    '''
    API View to remove a user from a team
    Accepts: user_id, team_id
    Available to: Superuser (for all teams), Team leader (for their team)
    Method: POST
    '''
    class InputSerializer(serializers.Serializer):
        user_id = serializers.IntegerField(required=True)
        team_id = serializers.IntegerField(required=True)

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated] # removed IsAdminUser permission since team leaders can also remove users from team
    serializer_class = InputSerializer

    def post(self, request , *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user_id = serializer.validated_data['user_id']
        team_id = serializer.validated_data['team_id']
        response = remove_team_from_user(user_id=user_id, team_id=team_id, auth_user=request.user)
        return Response(response, status=status.HTTP_200_OK)

class UpdateAccountType(generics.GenericAPIView):
    '''
    API View to update a user's account type
    Accepts: user_id, account_type
    Available to: Superuser
    METHOD: POST
    '''
    class InputSerializer(serializers.Serializer):
        user_id = serializers.IntegerField(required=True)
        account_type = serializers.CharField(required=True)

        def validate(self, attrs):
            """
            Check if the account type is valid or not 
            """
            if attrs['account_type'] not in ['W', 'C', 'T', 'S']:
                raise serializers.ValidationError("Invalid account type")
            return super().validate(attrs)

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = InputSerializer

    def post(self, request , *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user_id = serializer.validated_data['user_id']
        account_type = serializer.validated_data['account_type']
        response = update_account_type(user_id=user_id, account_type=account_type, auth_user=request.user)
        return Response(response, status=status.HTTP_200_OK)


class DisableAccount(generics.GenericAPIView):
    '''
    API View to disable a user's account
    Accepts: user_id
    Available to: Superuser (for all teams)
    Method: POST
    '''
    class InputSerializer(serializers.Serializer):
        user_id = serializers.IntegerField(required=True)

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = InputSerializer

    def post(self, request , *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user_id = serializer.validated_data['user_id']
        response = disable_account(user_id=user_id, auth_user=request.user)
        return Response(response, status=status.HTTP_200_OK)

    
class UserListView(generics.ListAPIView):
    '''
    API View to get active user list
    Available to: authenticated users
    Method: GET
    '''
    class UserSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ('pk', 'username', 'email')

    queryset = User.objects.all().filter(deleted_at__isnull=True)
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class RegisterUser(generics.CreateAPIView):
    '''
    API View to register a new user
    Available to: open to all
    Method: POST
    '''
    class UserSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ('pk', 'username', 'email', 'password')

        def create(self, validated_data, *args, **kwargs):
            user = User.objects.create_user(**validated_data)
            user.set_password(validated_data['password'])
            user.save(*args, **kwargs)
            return user

    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        user = User.objects.get(username=serializer.data['username'])
        # ACTION: generate refresh token and access token for the user
        refresh = RefreshToken.for_user(user) 
        headers = self.get_success_headers(serializer.data)
        return Response(
            {"data": serializer.data, "refresh": str(refresh), "access": str(refresh.access_token)},
            status=status.HTTP_201_CREATED, 
            headers=headers,
            )
