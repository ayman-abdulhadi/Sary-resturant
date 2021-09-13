from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from users.serializers import UserSerializer
from users.permissions import IsAdminOrReadOnly


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, IsAdminOrReadOnly)
