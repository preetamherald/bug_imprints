from django.apps import apps
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth.hashers import make_password

from django.utils.translation import gettext_lazy as _

from django.utils import timezone
from tracker.middlewares import get_request

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

# Create your models here.

class User(AbstractUser):
    '''
    Custom User Model, 
    with email as the unique identifier instead of username,
    and maintains record of creator, modifier and deleter of the object

    '''
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
    
    def save(self, auth_user = None, *args, **kwargs):
        '''
        set the created_by and modified_by to the user who is creating the object if it's available.
        and keeps updating the modified_by to the user who is modifying the object with the current time.

        if the method is called via request, the user will be fetched from the request object, no need to pass the user_id.
        if the method is called via shell, then the "auth_user=user_id" should be passed to the function.
        if no user_id is passed, then it shall be treated as user created by systm or registration form 
        and the created_by and modified_by will be set to none.
        '''
        if auth_user is not None:
            # CASE: if user is passes as arguement, assign it
            self.modified_by = auth_user
        else:
            req = get_request()
            if req is not None:
                auth_user = getattr(req, 'user', None)
                # CHECK: if logged in user is not anonymous user.
                if auth_user.is_anonymous is False:
                    if self._state.adding:
                        # CASE: if new object, set both created_by and modified_by to auth_user
                        self.created_by = auth_user
                        self.modified_by = auth_user
                    else:
                        # CASE: if existing object, only update the modified_by
                        self.modified_by = auth_user
        # if no user is passed, then it shall be treated as user created by systm or registration form
        # and the created_by and modified_by will be set to none.
        # TODO: set created_by and modified_by to self if no user is passed
        return super(User,self).save(*args, **kwargs)
    
    def soft_delete(self, auth_user = None, *args, **kwargs):
        '''
        set the deleted_by to the user who is deleting the object and set the deleted_at to the current time.

        if the method is called via request, the user will be fetched from the request object, no need to pass the user_id.
        if the method is called via shell, then the "auth_user=user_id" should be passed to the function.
        '''
        if auth_user is not None:
            # CASE: if user is passes as arguement, assign it
            self.deleted_by = auth_user
            self.modified_by = auth_user
        else:
            req = get_request()
            if req is not None:
                # CASE: Request is unavailable and auth_user is not passed
                # Inference: The method is called via shell, so auth_user is required
                # Solution: Raise an error
                # Alternative: TODO: Check if we can send a login request in shell 
                return ValueError("kindly provide auth_user") 
            auth_user = getattr(req, 'user', None)
            if auth_user.is_anonymous is True:
                # CASE: user is not logged in
                # Solution: Raise an error
                # Remark: This block running indicates some APIs are not protected
                raise ValueError("Please login and try again")
        self.deleted_by = auth_user
        self.modified_by = auth_user                            
        self.deleted_at = timezone.now()
        return self.save(auth_user=auth_user, *args, **kwargs)

    @property
    def get_active_teams_list(self):
        '''
        Returns queryset of active Team list of the user: Teams model.
        '''
        return self.teams.all().filter(deleted_at__isnull=True)

    