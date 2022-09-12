from django.apps import apps
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth.hashers import make_password

from django.utils.translation import gettext_lazy as _

from django.utils import timezone
from tracker.middlewares import get_request

# from tracker.models import BaseModel as CustomBaseModel, SoftDeleteModel


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not username:
            raise ValueError("The given username must be set")
        email = self.normalize_email(email)
        # Lookup the real model class from the global app registry so this
        # manager method can be used in migrations. This is fine because
        # managers are by definition working on the real model.
        GlobalUserModel = apps.get_model(
            self.model._meta.app_label, self.model._meta.object_name
        )
        username = GlobalUserModel.normalize_username(username)
        force_insert = extra_fields.pop("force_insert", False)
        user = self.model(username=username, email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db,force_insert=force_insert)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(username, email, password, force_insert= True, **extra_fields) #restrict force user to this function call only


    # def create_user(self, email, username=None, password=None, first_name=None, last_name=None, *args, **kwargs):
    #     if email is None:
    #         raise TypeError('Users must have an email address.')

    #     user = self.model(email=self.normalize_email(email))
    #     user.set_password(password)

    #     GlobalUserModel = apps.get_model(
    #         self.model._meta.app_label, self.model._meta.object_name
    #     )
    #     username = GlobalUserModel.normalize_username(username)

    #     user.username = username
    #     user.first_name = first_name
    #     user.last_name = last_name
    #     user.save(**kwargs)

    #     return user

    # def create_superuser(self, email, password, username=None, first_name=None, last_name=None):
    #     if password is None:
    #         raise TypeError('Superusers must have a password.')
    #     user = self.create_user(email, username, password, first_name, last_name , force_insert= True)
    #     user.is_superuser = True
    #     user.is_staff = True
    #     user.save(force_insert= True)
    #     return user


# Create your models here.

class User(AbstractUser):
    email = models.EmailField(_("email address"), blank=False, null=False,unique=True)
    account_type = models.CharField(max_length=1,blank=False, null=False, default = 'W', choices=(('W', 'Watcher'), ('C', 'Contributor'), ('T', 'Team Leader'), ('S', 'Superuser'),))
    teams = models.ManyToManyField('tracker.Teams', related_name='users', blank=True)

    icon = models.ImageField(upload_to='user_icons', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('self', related_name='%(class)s_created', on_delete=models.RESTRICT, null=True, blank=True)
    modified_by = models.ForeignKey('self', related_name='%(class)s_modified', on_delete=models.RESTRICT, null=True, blank=True)

    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey('self', related_name='%(class)s_deleted', on_delete=models.RESTRICT, null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
       
    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
    
    def __str__(self):
        return getattr(self, self.USERNAME_FIELD)
    
    def get_full_name(self):
        return self.first_name + " " + self.last_name

    def clean(self) -> None:
        super().clean()
        self.first_name = self.first_name.title()
        self.last_name = self.last_name.title()
    
    def save(self, auth_user = None, *args, **kwargs):          # if calling via shell, user_id should be passed to the function.
        if auth_user is not None:
            self.modified_by = auth_user
        else:
            req = get_request()
            if req is not None:
                auth_user = getattr(req, 'user', None)
                if auth_user.is_anonymous is False:
                    if self._state.adding:                          # if new object, set both created_by and modified_by to auth_user
                        self.created_by = auth_user
                        self.modified_by = auth_user
                    else:                                           # if existing object, only update the modified_by
                        self.modified_by = auth_user
        return super(User,self).save(*args, **kwargs)           # if no auth_user is given, save without setting created_by or modified_by, since user can register themselves, that implies they are the creator and modifier.

    
    def soft_delete(self, auth_user = None, *args, **kwargs):   # if calling via shell, user_id should be passed to the function.
        if auth_user is not None:                               # if user is passes as arguement, assign it
            self.deleted_by = auth_user
            self.modified_by = auth_user
        else:
            req = get_request()
            if req is not None:
                return ValueError("kindly provide auth_user")   # This case is possibe in case of shell use, ask user to provide required field, alternatively can give a cmd form to login in shell                                                   
            auth_user = getattr(req, 'user', None)
            if auth_user.is_anonymous is True:                               # this case can happed incase a not logged in user requests for deletion using any bug
                raise ValueError("Please login and try again")
        self.deleted_by = auth_user
        self.modified_by = auth_user                            # if user is not available in request, then it is a shell call, do not update deleted_by and modified_by
        self.deleted_at = timezone.now()                        # set deleted_at to current time
        return self.save(auth_user=auth_user, *args, **kwargs)  # save the model

       
                # raise ValueError("Please Login & Try again.")
        # if auth_user.is_superuser == False:                                   # permissions to be checked outside models.py
        #    raise ValueError("You are not authorized to delete this user.")
        # self.deleted_by = auth_user
        # self.modified_by = auth_user

        # if auth_user is None:
        #     req = get_request()
        #     if req is None:
        #         return '{"error": "user_id is None, Kindly login and try again"}'
        #     auth_user = req.user
        # self.deleted_at = timezone.now()
        # self.deleted_by_id = auth_user ## TODO find a way to get user id here to make this function independent from user input. DONE
        # self.save(auth_user = auth_user, *args, **kwargs)

    @property
    def get_active_teams_list(self):
        return self.teams.all().filter(deleted_at__isnull=True)

    