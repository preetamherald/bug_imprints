from django.urls import path

from . views import TeamsList, TeamsDetail, BugList, BugDetail, BugResolutionList, BugResolutionDetail, MessegeCreate, MessegeDestroy, TeamBugResolutionList, MediaUpload

urlpatterns = [

    path('teams/', TeamsList.as_view()), #OK
    path('teams/<id>/', TeamsDetail.as_view()), #OK
    path('teams/bugResolution/<id>/', TeamBugResolutionList.as_view()), #OK
    path('bugs/', BugList.as_view()),
    path('bugs/<id>/', BugDetail.as_view()),
    path('bugResolution/', BugResolutionList.as_view()),
    path('bugResolution/<id>/', BugResolutionDetail.as_view()),
    
    path('etc/upload/', MediaUpload.as_view()),
    path('etc/comments/add/', MessegeCreate.as_view()),
    path('etc/comments/<id>/', MessegeDestroy.as_view()),
    ]
