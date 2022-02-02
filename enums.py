from enum import Enum


class AccountTypeEnum(Enum):
    ADMIN    = 0
    CREATOR  = 1
    CONSUMER = 2


class SocialSignUpTypeEnum(Enum):
    NO_SOCIAL = 0
    KAKAO     = 1
    NAVER     = 2
    FACEBOOK  = 3
    GOOGLE    = 4
    APPLE     = 5
