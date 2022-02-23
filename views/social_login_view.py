import traceback
import requests

from django.conf                import settings
from django.shortcuts           import redirect
from rest_framework             import status
from rest_framework.response    import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators  import api_view, permission_classes

from common.const               import ResponseMsgConst, ResponseErrMsgConst
from common.utils               import CommonUtil
from common.exceptions          import (
    RequestsError
)


@api_view(['GET'])
@permission_classes([AllowAny])
def kakao_authorization_code(request):
    """ 카카오 인가 코드 취득
        # Todo Redirect Error Page
    """
    HOST         = settings.KAKAO_HOST
    CLIENT_ID    = settings.KAKAO_REST_API_KEY
    REDIRECT_URI = settings.KAKAO_SIGNUP_REDIRECT_URI
    
    if request.method != 'GET':
        return redirect('')
    
    try:
        redirect_url = f'{HOST}/oauth/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code'
        return redirect(redirect_url)
        
    except RequestsError:
        traceback.print_exc()
        return redirect('')


@api_view(['GET'])
@permission_classes([AllowAny])
def kakao_authorization_code_callback(request):
    """ 카카오 인가 코드 취득 콜백 API. 엑세스 토큰 및 리프레쉬 토큰 받아 리턴
        request.query_params
        - code : 카카오 인가 코드
        
        return
        - success
            {
                'token_type'              : '',
                'access_token'            : '',
                'expires_in'              : '',
                'refresh_token'           : '',
                'refresh_token_expires_in': '',
                'scope'                   : ''
            }
        
        - fail
            {
                'error'            : 'invalid_grant',
                'error_description': 'authorization code not found for code=RjIT4...',
                'error_code'       : 'KOE320'
            }
    """
    if request.method != 'GET':
        return Response(
            CommonUtil.return_data(err_msg=ResponseMsgConst.NOT_ALLOWED_REQUEST_TYPE),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    return_data = dict()
    HOST         = settings.KAKAO_HOST
    CLIENT_ID    = settings.KAKAO_REST_API_KEY
    REDIRECT_URI = settings.KAKAO_SIGNUP_REDIRECT_URI
    
    try:
        code = request.query_params['code']
        
        request_url = f'{HOST}/oauth/token?grant_type=authorization_code&client_id={CLIENT_ID}&' \
                      f'redirect_uri={REDIRECT_URI}&code={code}'
        
        result = requests.get(request_url).json()
        error  = result.get('error')
        
        if error:
            raise RequestsError(result.get('error_code'))
        
        return_data['access_token'] = result['access_token']
        
        return Response(
            CommonUtil.return_data(msg=ResponseMsgConst.SUCCESS, data=return_data),
            status=status.HTTP_200_OK
        )
        
    except KeyError:
        traceback.print_exc()
        return Response(
            CommonUtil.return_data(err_msg=ResponseErrMsgConst.KEY_ERROR),
            status=status.HTTP_400_BAD_REQUEST
        )
        
    except RequestsError as e:
        return Response(
            CommonUtil.return_data(err_msg=str(e)),
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )


@api_view(['POST'])
def kakao_profile(request):
    """ 카카오 프로필 정보 취득. 이메일 정보 취득 후 리턴하여 회원가입 또는 로그인 진행
        request.data
        - access_token
        
        return
        - email
    """
    if request.method != 'POST':
        return Response(
            CommonUtil.return_data(err_msg=ResponseMsgConst.NOT_ALLOWED_REQUEST_TYPE),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    return_data = dict()
    
    try:
        url          = 'https://kapi.kakao.com/v2/user/me'
        access_token = request.data['access_token']
        
        headers = {
            'Authorization': f"Bearer {access_token}",
            'Content-Type' : 'application/x-www-form-urlencoded;charset=utf-8'
        }
        
        profile_info = requests.get(url, headers=headers).json()
        return_data['email'] = profile_info['kakao_account']['email']
        
        return Response(
            CommonUtil.return_data(msg=ResponseMsgConst.SUCCESS, data=return_data),
            status=status.HTTP_200_OK
        )
        
    except KeyError:
        traceback.print_exc()
        return Response(
            CommonUtil.return_data(msg=ResponseErrMsgConst.KEY_ERROR),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    except RequestsError as e:
        traceback.print_exc()
        return Response(
            CommonUtil.return_data(err_msg=str(e)),
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
