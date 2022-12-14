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







# router = DefaultRouter()
# router.register('bug', bugsViewSet, basename='bug')
# router.register('teams', teamsViewSet, basename='teams')
# router.register('user', userViewSet, basename='user')
# router.register('mediastore', mediaStoreViewSet, basename='mediastore')
# router.register('messeges', messegesViewSet, basename='messeges')
# router.register('bugresolution', bugResolutionViewSet, basename='bugresolution')
# router.register('bugwatch', bugWatchViewSet, basename='bugwatch')
# router.register('bugduplicate', bugDuplicateViewSet, basename='bugduplicate')


# urlpatterns = [
#     path('teams', TeamViewSet.as_view({'get': 'list'})),
#     path('user', UserViewSet.as_view({'get': 'list'}), name='user'),
#     # path('', include(router.urls)),
#     # path('add/', postData),
#     # path('bug/', bug_list),
#     # path('', TeamsListApiView.as_view()),
    # path('', include(router.urls)),

# ]
