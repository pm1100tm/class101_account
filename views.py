import traceback

from django.db                                  import transaction, DatabaseError
from django.http                                import Http404
from rest_framework                             import viewsets, status, permissions
from rest_framework.response                    import Response
from rest_framework.serializers                 import ValidationError

from account.serializers.user_signup_serializer import UserSignUpSerializer
from account.models                             import User, AccountTypes

from account.utils import print_request_body


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
        """
        print(f"{'*'*30} create:: {print_request_body(request.data)}")
        try:
            data = {
                'email'             : request.data['email'].strip(),
                'password'          : request.data['password'].strip(),
                'social_signup_type': int(request.data['social_signup_type']),
                'account_type' : int(request.data['account_type']),
            }
            
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            
        except KeyError as e:
            traceback.print_exc()
            return Response('-')
        
        except Exception:
            traceback.print_exc()
            return Response('-')
    
    def retrieve(self, request, *args, **kwargs):
        try:
            print(f"{'*' * 30} retrieve:: {kwargs}")
            instance   = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except (AttributeError, ValueError):
            traceback.print_exc()
            return Response({'msg': 'test'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def list(self, request, *args, **kwargs):
        print('*'*30, 'list')
        queryset = self.queryset
        
        if not queryset:
            return Response({'msg' : 'NO_CONTENT'}, status=status.HTTP_200_OK)
            
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def update(self, request, *args, **kwargs):
        pass


