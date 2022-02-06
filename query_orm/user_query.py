from django.db.models import QuerySet
from account.models   import User


class UserDatabaseQuery:
    
    def get_user_by_email(self, email: str=None) -> QuerySet:
        user = User.objects.filter(email=email)
        return user
    
    def check_user_email(self, email: str=None) -> bool:
        user = User.objects.filter(email=email)
        return user.exists()
    
    def check_user_alive(self, email: str=None) -> bool:
        user = User.objects.filter(is_deleted=False, email=email)
        return user.exists()
