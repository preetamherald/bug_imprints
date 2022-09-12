from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from user.views import AddUserToTeam, RemoveUserFromTeam, UpdateAccountType, DisableAccount, UserListView, RegisterUser

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/',RegisterUser.as_view()),

    path('extras/userList/', UserListView.as_view()),
    path('extras/assignTeam/', AddUserToTeam.as_view()),
    path('extras/unsassignTeam/', RemoveUserFromTeam.as_view()),
    path('extras/updateAccountType/', UpdateAccountType.as_view()),
    path('extras/disableAccount/', DisableAccount.as_view()),
]
