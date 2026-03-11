from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from core.rbac import get_user_role


class RoleTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = get_user_role(user)
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["role"] = get_user_role(self.user)
        return data
