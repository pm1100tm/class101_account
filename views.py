import traceback
import requests

from django.conf                                import settings
from django.db                                  import transaction, DatabaseError
from django.shortcuts                           import redirect

from rest_framework                             import viewsets, status
from rest_framework.response                    import Response
from rest_framework.decorators                  import action
from rest_framework.serializers                 import ValidationError

from account.serializers.user_serializers       import *
from account.enums                              import SocialSignUpTypeEnum, AccountTypeEnum
from account.query_orm.user_query               import UserDatabaseQuery
from common.const                               import AppNameConst, MethodNameConst, ResponseMsgConst
from common.utils                               import CommonUtil
from common.exceptions                          import (
    KakaoCallbackError,
    NotNullException,
    UserExistsException,
    UserNotExistsException,
    UserDeletedException,
    PasswordNotCorrectException
)


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserCreateSerializer
    user_query       = UserDatabaseQuery()
    
    def get_queryset(self):
        queryset = User.objects.filter(is_deleted=False)
        return queryset
    
    @action(detail=False, methods=['get'], url_path='sign-up/kakao')
    def signup_kakao(self, request):
        """ 카카오 인가 코드 취득
        """
        CommonUtil.print_log(app_name=AppNameConst.ACCOUNT, method_name=MethodNameConst.SIGN_UP_KAKAO, request_param=request.query_params, class_=self)
        HOST         = settings.KAKAO_HOST
        CLIENT_ID    = settings.KAKAO_REST_API_KEY
        REDIRECT_URI = settings.KAKAO_SIGNUP_REDIRECT_URI
        
        try:
            redirect_url = f'{HOST}/oauth/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code'
            return redirect(redirect_url)
        
        except Exception as e:
            print(str(e))
            traceback.print_exc()
            # Todo Error Page URL
            return redirect('')
    
    @action(detail=False, methods=['get'], url_path='sign-up/kakao-callback')
    def signup_kakao_callback(self, request):
        """ 카카오 콜백. 엑세스 토큰 및 리프레쉬 토큰 받아 리턴
            Response Success Example
            {
                'token_type'              : '',
                'access_token'            : '',
                'expires_in'              : '',
                'refresh_token'           : '',
                'refresh_token_expires_in': '',
                'scope'                   : ''
            }

            Response Fail Example
            {
                'error'            : 'invalid_grant',
                'error_description': 'authorization code not found for code=RjIT4...',
                'error_code'       : 'KOE320'
            }
        """
        CommonUtil.print_log(app_name=AppNameConst.ACCOUNT, method_name=MethodNameConst.SIGN_UP_KAKAO_CALLBACK, request_param=request.query_params, class_=self)
        return_data  = dict()
        HOST         = settings.KAKAO_HOST
        CLIENT_ID    = settings.KAKAO_REST_API_KEY
        REDIRECT_URI = settings.KAKAO_SIGNUP_REDIRECT_URI
        
        try:
            code = request.query_params['code']
            
            request_url = f'{HOST}/oauth/token?grant_type=authorization_code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&code={code}'
            result = requests.get(request_url).json()
            
            error = result.get('error')
            if error:
                raise KakaoCallbackError
            
            return_data['access_token'] = result['access_token']
            
            result = CommonUtil.return_data(msg=ResponseMsgConst.SUCCESS,
                                            data=return_data)
            
            return Response(result, status=status.HTTP_200_OK)
            
        except KeyError:
            traceback.print_exc()
            result = CommonUtil.return_data(msg=ResponseMsgConst.KEY_ERROR)
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        except KakaoCallbackError as e:
            result = CommonUtil.return_data(msg=str(e))
            return Response(result, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        except Exception as e:
            print(str(e))
            traceback.print_exc()
            result = CommonUtil.return_data(msg=ResponseMsgConst.FAIL)
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'], url_path='sign-up/kakao-profile')
    def signup_kakao_get_profile(self, request):
        """ 카카오 프로필 정보 취득. 이메일 정보 취득 후 리턴하여 회원가입 또는 로그인 진행
        """
        CommonUtil.print_log(app_name=AppNameConst.ACCOUNT, method_name=MethodNameConst.SIGN_UP_KAKAO_GET_PROFILE, request_data=request.data, class_=self)
        return_data = dict()
        
        try:
            access_token = request.data['access_token']
            url = 'https://kapi.kakao.com/v2/user/me'
            headers = {
                'Authorization': f"Bearer {access_token}",
                'Content-Type' : 'application/x-www-form-urlencoded;charset=utf-8'
            }
            profile_info = requests.get(url, headers=headers).json()
            
            return_data['email'] = profile_info['kakao_account']['email']
            
            result = CommonUtil.return_data(msg=ResponseMsgConst.SUCCESS,
                                            data=return_data)
            
            return Response(result, status=status.HTTP_200_OK)
            
        except KeyError:
            traceback.print_exc()
            result = CommonUtil.return_data(msg=ResponseMsgConst.KEY_ERROR)
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            print(str(e))
            traceback.print_exc()
            result = CommonUtil.return_data(msg=ResponseMsgConst.FAIL)
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'], url_path='sign-in')
    def sign_in(self, request):
        """ 유저 로그인 (컨슈머 only)
            일반 로그인
             - email, password, social_signup_type 필수
            
            소셜 로그인
             - email, social_signup_type 필수
        """
        CommonUtil.print_log(app_name=AppNameConst.ACCOUNT, method_name=MethodNameConst.SIGN_IN, request_data=request.data, class_=self)
        
        # Todo list
        # 1. JWT or DRF AuthToken
        # 2. add login count, last login time column
        # 3. insert consumer model with transaction atomic
        
        try:
            # 입력 값 편집
            data = {
                'email'              : request.data['email'].strip(),
                'password'           : request.data.get('password').strip() if request.data.get('password') else None,
                'social_signup_type' : int(request.data['social_signup_type']),
                'account_type'       : AccountTypeEnum.CONSUMER.value # 고정 값
            }
            
            # 상관관계 유효성 체크
            if SocialSignUpTypeEnum.NO_SOCIAL.value == data['social_signup_type']:
                if not data['password']:
                    raise NotNullException('password')
            
            user = self.user_query.get_user_by_email(email=data['email'])
            if not user.exists():
                raise UserNotExistsException
            
            user_obj: User = user.first()
            is_deleted     = user_obj.is_deleted
            
            if is_deleted:
                raise UserDeletedException
            
            if data['password'] != user_obj.password:
                raise PasswordNotCorrectException
            
            self.user_query.increase_login_count(user=user_obj)
            
            serializer = UserInfoSerializer(user_obj)
            result     = CommonUtil.return_data(msg=ResponseMsgConst.SUCCESS,
                                                data=serializer.data)
            
            return Response(result, status=status.HTTP_200_OK)
            
        except UserNotExistsException as e:
            result = CommonUtil.return_data(msg=str(e))
            return Response(result, status=status.HTTP_409_CONFLICT)
        
        except PasswordNotCorrectException as e:
            result = CommonUtil.return_data(msg=str(e))
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
    
    def create(self, request, *args, **kwargs):
        """ 유저 회원가입 (컨슈머 생성)
            request body
            - email : str
            - password : str
            - social_signup_type : int
        """
        CommonUtil.print_log(app_name=AppNameConst.ACCOUNT, method_name=MethodNameConst.CREATE, request_data=request.data, class_=self)
        
        try:
            # 입력 값 편집
            data = {
                'email'             : request.data['email'].strip(),
                'password'          : request.data.get('password').strip() if request.data.get('password') else None,
                'social_signup_type': int(request.data['social_signup_type']),
                'account_type'      : AccountTypeEnum.CONSUMER.value # 고정 값
            }
            
            # 상관관계 유효성 체크
            if SocialSignUpTypeEnum.NO_SOCIAL.value == data['social_signup_type']:
                if not data['password']:
                    raise NotNullException('password')
            
            user = self.user_query.get_user_by_email(email=data['email'])
            if user.exists():
                
                user_obj: User = user.first()
                is_deleted = user_obj.is_deleted
                
                if is_deleted:
                    raise UserDeletedException
                
                if not is_deleted:
                    raise UserExistsException
            
            # Field Level validation 및 DB 처리 (is_valid 에서 자동으로 해당 모델 필드의 유니크, 필수, 존재 여부를 체크하나
            # 리턴 포멧이 일정하지 않게 되어 커스터마이징 필요
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            
            result = CommonUtil.return_data(msg=ResponseMsgConst.SUCCESS)
            return Response(result, status=status.HTTP_201_CREATED)
            
        except KeyError:
            traceback.print_exc()
            result = CommonUtil.return_data(msg=ResponseMsgConst.KEY_ERROR)
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
        except UserExistsException as e:
            result = CommonUtil.return_data(msg=str(e))
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
        except UserDeletedException as e:
            result = CommonUtil.return_data(msg=str(e))
            return Response(result, status=status.HTTP_204_NO_CONTENT)
        
        except DatabaseError:
            result = CommonUtil.return_data(msg=ResponseMsgConst.KEY_ERROR)
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def retrieve(self, request, *args, **kwargs):
        CommonUtil.print_log(app_name=AppNameConst.ACCOUNT, method_name=MethodNameConst.RETRIEVE, request_data=kwargs, class_=self)
        
        try:
            instance   = self.get_object()
            serializer = self.get_serializer(instance)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except (AttributeError, ValueError):
            traceback.print_exc()
            result = CommonUtil.return_data(msg=ResponseMsgConst.ATTRIBUTE_VALUE_ERROR)
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
    
    def list(self, request, *args, **kwargs):
        CommonUtil.print_log(app_name=AppNameConst.ACCOUNT, method_name=MethodNameConst.LIST, request_data=kwargs, class_=self)
        queryset = self.queryset
        
        if not queryset:
            result = CommonUtil.return_data(msg=ResponseMsgConst.NO_CONTENT)
            return Response(result, status=status.HTTP_200_OK)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def update(self, request, *args, **kwargs):
        CommonUtil.print_log(app_name=AppNameConst.ACCOUNT, method_name=MethodNameConst.UPDATE, request_data=request.data, class_=self)
        pass

