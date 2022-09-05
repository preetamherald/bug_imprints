from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User


from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView


from .serializers import TeamsSerializer, BugSerializer, UserSerializer, MediaStoreSerializer, MessegesSerializer, BugResolutionSerializer, BugWatchSerializer, BugDuplicateSerializer
from tracker.models import Teams, Bug, MediaStore, Messeges, BugResolution, BugWatch, BugDuplicate


class userViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

class bugsViewSet(viewsets.ModelViewSet):
    queryset = Bug.objects.all().filter(deleted_at__isnull=True)
    serializer_class = BugSerializer
    permission_classes = [permissions.IsAuthenticated]

class teamsViewSet(viewsets.ModelViewSet):
    queryset = Teams.objects.all().filter(deleted_at__isnull=True)
    serializer_class = TeamsSerializer
    permission_classes = [permissions.IsAuthenticated]

class mediaStoreViewSet(viewsets.ModelViewSet):
    queryset = MediaStore.objects.all().filter(deleted_at__isnull=True)
    serializer_class = MediaStoreSerializer
    permission_classes = [permissions.IsAuthenticated]

class messegesViewSet(viewsets.ModelViewSet):
    queryset = Messeges.objects.all().filter(deleted_at__isnull=True)
    serializer_class = MessegesSerializer
    permission_classes = [permissions.IsAuthenticated]

class bugResolutionViewSet(viewsets.ModelViewSet):
    queryset = BugResolution.objects.all().filter(deleted_at__isnull=True)
    serializer_class = BugResolutionSerializer
    permission_classes = [permissions.IsAuthenticated]

class bugWatchViewSet(viewsets.ModelViewSet):
    queryset = BugWatch.objects.all().filter(deleted_at__isnull=True)
    serializer_class = BugWatchSerializer
    permission_classes = [permissions.IsAuthenticated]

class bugDuplicateViewSet(viewsets.ModelViewSet):
    queryset = BugDuplicate.objects.all().filter(deleted_at__isnull=True)
    serializer_class = BugDuplicateSerializer
    permission_classes = [permissions.IsAuthenticated]






# ------------------ API Views ------------------ #


# @api_view(['GET', 'POST'])
# def bugsApiView(request):
#     if (request.method == 'GET'):
#         bugs = Bug.objects.all().filter(deleted_at__isnull=True)
#         serializer = BugSerializer(bugs, many=True)
#         return Response(serializer.data)

#     elif (request.method == 'POST'):
#         serializer = BugSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=201)
#         return Response(serializer.errors, status=400)

# @api_view(['GET', 'POST'])
# def teamApiView(request):
#     if (request.method == 'GET'):
#         teams = Teams.objects.all().filter(deleted_at__isnull=True)
#         serializer = TeamsSerializer(Teams, many=True)
#         return Response(serializer.data)

#     elif (request.method == 'POST'):
#         serializer = TeamsSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=201)
#         return Response(serializer.errors, status=400)



# class TeamsListApiView(APIView):
#     # add permission to check if user is authenticated
#     permission_classes = [permissions.IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         teams = Teams.objects.all().filter(deleted_at__isnull=True)
#         serializer = TeamsSerializer(teams, many=True, context={'request': request})
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     def post(self, request, *args, **kwargs):

#         data = {
#             'team_name': request.data.get('team_name'),
#             'team_leader': request.data.get('team_leader'),
#         }
#         serializer = TeamsSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class UserListApiView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         users = User.objects.all().filter(deleted_at__isnull=True)
#         serializer = UserSerializer(users, many=True, context={'request': request})
#         return Response(serializer.data, status=status.HTTP_200_OK)


# # Create your views here.

# @api_view(['GET'])
# def getData(request):
#     teams = Teams.objects.all()
#     serializer = TeamsSerializer(teams, many=True)
#     return Response(serializer.data)

# @api_view(['POST'])
# def postData(request):
#     serializer = TeamsSerializer(data=request.data)
#     if serializer.is_valid():
#         serializer.save()
#     return Response(serializer.data)




# # ----------------------------------------------------------------- #

# @login_required
# @api_view(['GET', 'POST'])
# def bug_list(request, acceptance = None):
#     if (request.method == 'GET'):
#         bugs = Bug.objects.all().filter(acceptance=acceptance, deleted_at__isnull=True)
#         serializer = BugSerializer(bugs, many=True)
#         return Response(serializer.data)

#     elif (request.method == 'POST'):
#         data = JSONParser().parse(request)
#         serializer = BugSerializer(data=data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=201)
#         return Response(serializer.errors, status=400)





# class UserViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows users to be viewed or edited.
#     """
#     queryset = User.objects.all().order_by('-date_joined')
#     serializer_class = UserSerializer

# class TeamViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows teams to be viewed or edited.
#     """
#     queryset = Teams.objects.all().filter(deleted_at__isnull=True)
#     serializer_class = TeamsSerializer

 # ----------------------------------------------------------------- #