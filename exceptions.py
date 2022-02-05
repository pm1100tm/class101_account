class KakaoCallbackError(Exception):
    
    def __init__(self, msg=None):
        super().__init__('카카오 로그인 콜백 에러')

