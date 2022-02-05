import traceback
import requests

from django.conf                                import settings
from django.db                                  import transaction, DatabaseError
from django.http                                import Http404
from django.shortcuts                           import redirect

from rest_framework                             import viewsets, status, permissions
from rest_framework.response                    import Response
from rest_framework.decorators                  import api_view
from rest_framework.serializers                 import ValidationError

from account.serializers.user_signup_serializer import UserSignUpSerializer
from account.models                             import User, AccountTypes
from account.exceptions                         import KakaoCallbackError
from common.const                               import AppNameConst, MethodNameConst, ResponseMsgConst
from common.utils                               import CommonUtil


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSignUpSerializer
    
    def get_queryset(self):
        queryset = User.objects.filter(is_deleted=False)
        return queryset
    
    def create(self, request, *args, **kwargs):
        """ 유저 생성
            request body
            - email : str
            - password : str
            - social_signup_type : int
            - account_type : int
        """
        CommonUtil.print_log(app_name=AppNameConst.ACCOUNT, method_name=MethodNameConst.CREATE, request_data=request.data, class_=self)
        
        try:
            data = {
                'email'             : request.data['email'].strip(),
                'password'          : request.data.get('password').strip(),
                'social_signup_type': int(request.data['social_signup_type']),
                'account_type'      : int(request.data['account_type']),
            }
            
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            
            return Response(status=status.HTTP_201_CREATED, headers=headers)
            
        except KeyError:
            traceback.print_exc()
            result = CommonUtil.return_data(msg=ResponseMsgConst.KEY_ERROR)
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
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


@api_view(['GET'])
def signup_kakao(request):
    CommonUtil.print_log(app_name=AppNameConst.ACCOUNT, method_name=MethodNameConst.SIGN_UP_KAKAO, request_data=request.query_params)
    HOST         = settings.KAKAO_HOST
    CLIENT_ID    = settings.KAKAO_REST_API_KEY
    REDIRECT_URI = settings.KAKAO_SIGNUP_REDIRECT_URI
    
    try:
        redirect_url = f'{HOST}/oauth/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code'
        
        return redirect(redirect_url)
        
    except Exception as e:
        print(str(e))
        traceback.print_exc()
        #Todo Error Page URL
        return redirect('')

@api_view(['GET'])
def signup_kakao_callback(request):
    """ kakao login callback
        
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
    CommonUtil.print_log(app_name=AppNameConst.ACCOUNT, method_name=MethodNameConst.SIGN_UP_KAKAO_CALLBACK, request_data=request.query_params)
    return_data  = dict()
    HOST         = settings.KAKAO_HOST
    CLIENT_ID    = settings.KAKAO_REST_API_KEY
    REDIRECT_URI = settings.KAKAO_SIGNUP_REDIRECT_URI
    
    try:
        code        = request.query_params['code']
        request_url = f'{HOST}/oauth/token?grant_type=authorization_code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&code={code}'
        result      = requests.get(request_url).json()
        
        error = result.get('error')
        
        if error:
            raise KakaoCallbackError
        
        return_data['access_token'] = result['access_token']
        
        result = CommonUtil.return_data(msg =ResponseMsgConst.SUCCESS,
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


@api_view(['POST'])
def signup_kakao_get_profile(request):
    """ kakao get profile info
        Response Success Example {
            'id'                         : 99999999999,
            'connected_at'               : '2022-02-05T12:50:44Z',
            'properties'                 : {
                'nickname'               : 'OOO',
                'profile_image'          : 'http://k.kakaocdn.net/dn/cGcXAD/-.jpg',
                'thumbnail_image'        : 'http://k.kakaocdn.net/dn/cGcXAD/-.jpg'
            },
            'kakao_account'              : {
                'profile_needs_agreement': False,
                'profile'                : {
                    'nickname'           : 'OOO',
                    'thumbnail_image_url': 'http://k.kakaocdn.net/dn/cGcXAD/btrpmg6VjRT/-.jpg',
                    'profile_image_url'  : 'http://k.kakaocdn.net/dn/cGcXAD/btrpmg6VjRT/-.jpg',
                    'is_default_image'   : False
                },
                'has_email'              : True,
                'email_needs_agreement'  : False,
                'is_email_valid'         : True,
                'is_email_verified'      : True,
                'email'                  : 'OOO@OOO.com'
            }
        }
    """
    CommonUtil.print_log(app_name=AppNameConst.ACCOUNT, method_name=MethodNameConst.SIGN_UP_KAKAO_GET_PROFILE, request_data=request.data)
    return_data = dict()
    
    try:
        access_token = request.data['access_token']
        url          = 'https://kapi.kakao.com/v2/user/me'
        headers = {
            'Authorization': f"Bearer {access_token}",
            'Content-Type' : 'application/x-www-form-urlencoded;charset=utf-8'
        }
        
        profile_info = requests.get(url, headers=headers).json()
        
        return_data['email'] = profile_info['kakao_account']['email']
        
        result = CommonUtil.return_data(msg=ResponseMsgConst.SUCCESS,
                                        data=return_data)
        
        return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    except Exception as e:
        print(str(e))
        traceback.print_exc()
        result = CommonUtil.return_data(msg=ResponseMsgConst.FAIL)
        return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
