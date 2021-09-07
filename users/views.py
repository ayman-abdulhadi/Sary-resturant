from rest_framework import generics, permissions
from users.serializers import UserSerializer
from users.permissions import IsAdminOrReadOnly


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated, IsAdminOrReadOnly)
