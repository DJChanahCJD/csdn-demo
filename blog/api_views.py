from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Blog, Comment, Category
from .serializers import BlogSerializer, CommentSerializer, CategorySerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

# 前后端分离时使用
# API
# 该项目虽然使用了template，但是也试验了Django的API功能（首页的文章获取就使用了API）

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
    # @allowed_roles([Role.ADMIN, Role.DEVELOPER])
    def by_category(self, request):
        # blog/by-category?category_id=1
        
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

    # 自定义：搜索博客
    @action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        # /api/blogs/search/?q=搜索关键词
        query = request.query_params.get('q')
        if not query:
            return Response({'detail': '搜索关键词不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 使用Q对象进行标题和内容的模糊搜索
        from django.db.models import Q
        qs = self.get_queryset().filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )

        page = self.paginate_queryset(qs)
        serializer = self.get_serializer(page or qs, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.select_related('author', 'blog').all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
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