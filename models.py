from django.db import models


# class CertificationType(models.Model):
#     pass
#
#
# class PermissionType(models.Model):
#     pass
#
#
# class UserPermissionType(models.Model):
#     pass


class AccountTypes(models.Model):
    AC_TYPE = [
        (1, 'Admin'),
        (2, 'Creator'),
        (3, 'Consumer'),
    ]
    id   = models.PositiveSmallIntegerField(primary_key=True, choices=AC_TYPE)
    name = models.CharField(max_length=10)

    class Meta:
        db_table = 'account_types'


class SocialSignUpType(models.Model):
    SOCIAL_SIGNUP_TYPE = [
        (1, 'Kakao'),
        (2, 'Naver'),
        (3, 'Facebook'),
        (4, 'Google'),
        (5, 'Apple'),
    ]
    id   = models.PositiveSmallIntegerField(primary_key=True, choices=SOCIAL_SIGNUP_TYPE)
    name = models.CharField(max_length=50)
    
    class Meta:
        db_table = 'social_signup_types'


class User(models.Model):
    id                 = models.BigAutoField(primary_key=True)
    email              = models.EmailField(max_length=30, unique=True, verbose_name='이메일')
    password           = models.CharField(max_length=80, verbose_name='비밀번호')
    is_deleted         = models.BooleanField(default=False)
    created_at         = models.DateTimeField(auto_now=True, verbose_name='생성일')
    updated_at         = models.DateTimeField(auto_now_add=True, verbose_name='수정일')
    social_signup_type = models.ForeignKey('account.SocialSignUpType', null=True, on_delete=models.CASCADE, related_name='user')
    user_account_type  = models.ForeignKey('account.AccountTypes', on_delete=models.CASCADE, related_name='user')

    class Meta:
        db_table = 'users'


# class Consumer(models.Model):
#     pass
#
#
# class Creator(models.Model):
#     pass
