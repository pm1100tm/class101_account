from datetime         import datetime

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
    
    def increase_login_count(self, user: User, present_time: datetime) -> None:
        """ 유저가 로그인 했을 때 로그인 카운트와 마지막 로그인 시간 업데이트
        - login_count, last_login 컬럼만 업데이트 1 증가
        - login_count 1 증가, last_login 현재 시간으로 업데이트
            param
            - user: 유저 모델 인스턴스
            - present_time: 현재 시간 (datetime 객체)
            
            return
            - None
        """
        user.login_count += 1
        user.last_login_date = present_time
        user.save(update_fields=['login_count', 'last_login_date'])
