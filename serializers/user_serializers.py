from rest_framework             import serializers
from rest_framework.serializers import ValidationError

from account.models import User


class UserCreateSerializer(serializers.ModelSerializer):
    user_account_type_name  = serializers.SerializerMethodField()
    social_signup_type_name = serializers.SerializerMethodField()
    
    def get_user_account_type_name(self, obj: User):
        return obj.account_type.get_id_display()
    
    def get_social_signup_type_name(self, obj: User):
        return obj.social_signup_type.get_id_display()
    
    class Meta:
        model = User
        fields = (
            # model
            'id',
            'email',
            'password',
            'social_signup_type',
            'account_type',
            
            # define
            'user_account_type_name',
            'social_signup_type_name',
        )
        extra_kwargs = {
            'password'               : {'write_only': True},
            'user_account_type_name' : {'read_only' : True},
            'social_signup_type_name': {'read_only' : True}
        }


class UserInfoSerializer(serializers.ModelSerializer):
    user_account_type_name  = serializers.SerializerMethodField()
    social_signup_type_name = serializers.SerializerMethodField()
    
    def get_user_account_type_name(self, obj: User):
        return obj.account_type.get_id_display()
    
    def get_social_signup_type_name(self, obj: User):
        return obj.social_signup_type.get_id_display()
    
    class Meta:
        model  = User
        fields = (
            # model
            'id',
            'email',
            'is_deleted',
            
            # define
            'user_account_type_name',
            'social_signup_type_name',
        )
        extra_kwargs = {
            'id'                     : {'read_only': True},
            'email'                  : {'read_only': True},
            'is_deleted'             : {'read_only': True},
            'user_account_type_name' : {'read_only': True},
            'social_signup_type_name': {'read_only': True}
        }
