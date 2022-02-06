from django.db     import models
from account.const import UserConst


class AccountTypes(models.Model):
    id         = models.PositiveSmallIntegerField(primary_key=True, choices=UserConst.ACCOUNT_TYPE)
    name       = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now=True, verbose_name='생성일')
    
    class Meta:
        db_table = 'account_types'


class SocialSignUpType(models.Model):
    id         = models.PositiveSmallIntegerField(primary_key=True, choices=UserConst.SOCIAL_SIGNUP_TYPE)
    name       = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now=True, verbose_name='생성일')
    
    class Meta:
        db_table = 'social_signup_types'


class User(models.Model):
    id                 = models.BigAutoField(primary_key=True)
    email              = models.EmailField(max_length=30, unique=True, verbose_name='이메일')
    password           = models.CharField(max_length=80, null=True, verbose_name='비밀번호')
    # login_count        = models.IntegerField(default=0)
    # last_login_date    = models.CharField(max_length=19)
    is_deleted         = models.BooleanField(default=False)
    created_at         = models.DateTimeField(auto_now=True, verbose_name='생성일')
    updated_at         = models.DateTimeField(auto_now_add=True, verbose_name='수정일')
    account_type       = models.ForeignKey('account.AccountTypes', on_delete=models.CASCADE, related_name='user')
    social_signup_type = models.ForeignKey('account.SocialSignUpType', null=True, on_delete=models.CASCADE, related_name='user')
    
    class Meta:
        db_table = 'users'


# class Consumer(models.Model):
#     pass
# class Creator(models.Model):
#     pass
# class CertificationType(models.Model):
#     pass
# class PermissionType(models.Model):
#     pass
# class UserPermissionType(models.Model):
#     pass