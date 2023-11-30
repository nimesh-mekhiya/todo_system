from rest_framework import serializers
from .models import CustomUser, Todo, TodoSharing, TodoChangeLog, AccessLog

#User Serializers
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email')

#Register Serializers
class RegisterSerializers(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(validated_data['username'], validated_data['email'])
        user.set_password(validated_data['password'])
        user.save()
        return user

#Todo Serializers
class TodoSerializers(serializers.ModelSerializer):
    class Meta:
        model = Todo
        fields = ['id', 'title', 'category', 'due_date', 'status']

#Todo Sharing Serializers
class TodoSharingSerializer(serializers.ModelSerializer):
    class Meta:
        model = TodoSharing
        fields = ('id', 'todo', 'shared_with', 'access_type', 'approval_required', 'approved')

#Updating/Change any todo Serializers
class ChangeSharedTodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TodoChangeLog
        fields = ('id', 'todo', 'user', 'change_description', 'timestamp', 'approved_by_owner')

#Access Log Serializers
class AccessLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessLog
        fields = '__all__'