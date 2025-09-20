from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Blog, Comment, Category
from .serializers import BlogSerializer, CommentSerializer, CategorySerializer
from common.role import Role, allowed_roles
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class BlogViewSet(viewsets.ModelViewSet):
    queryset = Blog.objects.select_related('author').all()
    serializer_class = BlogSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    # # 例如：管理员/开发者可写
    # allowed_roles = {Role.ADMIN, Role.DEVELOPER}

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    # 自定义：按分类筛选（示例，等价于 filterset 的写法，便于上手）
    @action(detail=False, methods=['get'], url_path='by-category')
    # @allowed_roles([Role.ADMIN, Role.DEVELOPER, Role.ENTERPRISE])
    def by_category(self, request):
        # blog/by-category?category_id=1
        print(request.user)
        print('Auth:', request.headers.get('Authorization'))
        
        category_id = request.query_params.get('category_id')
        if not category_id:
            return Response({'detail': 'category_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        qs = self.get_queryset().filter(category_id=category_id)

        page = self.paginate_queryset(qs)
        print("page", page)
        serializer = self.get_serializer(page or qs, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.select_related('author', 'blog').all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    # 例如：所有登录用户可写（企业也可评论）
    # allowed_roles = {Role.ADMIN, Role.DEVELOPER, Role.ENTERPRISE}

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


@api_view(['POST'])
@permission_classes([AllowAny])
def custom_login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    # 使用email认证用户
    print("登录请求:", email, password)

    # 直接从数据库查询用户
    try:
        user = User.objects.get(email=email)
        # 验证密码
        if user.check_password(password):
            # 生成JWT令牌
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh_token': str(refresh),
                'access_token': str(refresh.access_token),
            })
        else:
            return Response({'detail': '密码错误'}, status=401)
    except User.DoesNotExist:
        return Response({'detail': '用户不存在'}, status=401)