from rest_framework import generics, permissions, viewsets, status
from rest_framework.response import Response
from rest_framework.authtoken.serializers import AuthTokenSerializer
from django.contrib.auth import login
from .serializers import *
from knox.models import AuthToken
from knox.views import LoginView as KnoxLoginView
from .models import Todo, TodoSharing, CustomUser, TodoChangeLog, AccessLog
from rest_framework.permissions import IsAuthenticated
from django.http import Http404

### Register API ###
class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializers

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({"user" : UserSerializer(user, context=self.get_serializer()).data,
                         "token" : AuthToken.objects.create(user)[1]
                         })
### Login API with Token Generation ###
class LoginAPI(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return super(LoginAPI, self).post(request, format)

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user

### CRUD of todo ###
class TodoViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    def get_object(self, pk):
        try:
            return Todo.objects.get(pk=pk)
        except Todo.DoesNotExist:
            raise Http404

    def list(self, request):
        todo_data = Todo.objects.filter(owner=request.user)
        serializer = TodoSerializers(todo_data, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        todo_data = self.get_object(pk)
        serializer = TodoSerializers(todo_data)
        return Response(serializer.data)

    def create(self, request):
        serializer = TodoSerializers(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
    def update(self, request, pk):
        todo_data = self.get_object(pk)
        self.check_object_permissions(self.request, todo_data)  # Checks if user owns the object
        serializer = TodoSerializers(todo_data, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"msg": "Complete Data Updated"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        todo_data = self.get_object(pk)
        self.check_object_permissions(request, todo_data)  # Checks if user owns the object
        serializer = TodoSerializers(todo_data, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"msg": "Partial Data Updated"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, pk=None):
        todo_data = self.get_object(pk)
        self.check_object_permissions(request, todo_data)  # Checks if user owns the object
        todo_data.delete()
        return Response({"msg": "Data Deleted"})

### This function sharing todo with users and
# User can give various access like read-only, read/write ###
class TodoSharingViewSet(viewsets.ViewSet):
    queryset = TodoSharing.objects.all()
    serializer_class = TodoSharingSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request):
        todo_id = request.data.get("todo")
        shared_with_id = request.data.get("shared_with")

        try:
            todo = Todo.objects.get(pk=todo_id)
            shared_with = CustomUser.objects.get(pk=shared_with_id)
        except (Todo.DoesNotExist, CustomUser.DoesNotExist):
            return Response({"error": "Todo or Shared User does not exist"}, status=status.HTTP_404_NOT_FOUND)

        serializer = TodoSharingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(todo=todo, shared_with=shared_with)

            # Log the activity
            activity_description = f"{request.user.username} shared '{todo.title}' with {shared_with.username}"
            AccessLog.objects.create(user=request.user, todo_sharing=serializer.instance, activity=activity_description)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

### This function inside updating shared todo.
# Also user have permisson of read and write it will be updating the todo ###
class ChangeSharedTodoViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)
    def create(self, request):
        todo_shared_id = request.data.get("todo")
        change_description = request.data.get("change_description")
        
        try:
            todo_sharing = TodoSharing.objects.get(pk=todo_shared_id)
        except TodoSharing.DoesNotExist:
            return Response({"message": "TodoSharing not found"}, status=status.HTTP_404_NOT_FOUND)

        # Check access_type
        if todo_sharing.access_type == "read_write":
            serializer = ChangeSharedTodoSerializer(data={
                'todo': todo_sharing.todo.id,
                'user': request.user.id,
                'change_description': change_description
            })
            if serializer.is_valid():
                serializer.save()
                # Log the activity
                AccessLog.objects.create(user=request.user,todo_sharing_id=todo_sharing.id,activity='Shared todo updated')
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "You do not have permission to modify this Todo"}, status=status.HTTP_403_FORBIDDEN)
        
### Here all the todo Changes request list showing to Owner of the Todo ###
class OwnerTodoChangeLogViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)
    def list(self, request):
        user_todos = Todo.objects.filter(owner=request.user)
        user_todo_sharing = TodoSharing.objects.filter(todo__in=user_todos)
        change_logs = TodoChangeLog.objects.filter(todo__in=user_todo_sharing.values_list('todo', flat=True))
        serializer = ChangeSharedTodoSerializer(change_logs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

### Any user changes the shared todo, the owner needs to approve and reject the changes ###
class ApproveChangeLogViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    def log_activity(self, user, todo_sharing, activity):
        AccessLog.objects.create(user=user, todo_sharing=todo_sharing, activity=activity)

    def update(self, request, pk=None):
        try:
            change_log = TodoChangeLog.objects.get(pk=pk)
        except TodoChangeLog.DoesNotExist:
            raise Http404("Change log does not exist")
            
        if request.user == change_log.todo.owner:
            status_val = request.data.get('status', None)
            if status_val in dict(TodoChangeLog.STATUS_CHOICES):
                if status_val == 'approve':
                    change_log.approved_by_owner = 'approve'
                    change_log.save()
                    # Log the activity
                    self.log_activity(request.user, None, f"Change log {pk} has been approved")
                    return Response({"message": f"Change log {pk} has been approved"})
                elif status_val == 'reject':
                    change_log.approved_by_owner = 'reject'
                    change_log.save()
                    # Log the activity for rejection
                    self.log_activity(request.user, None, f"Change log {pk} has been rejected")
                    return Response({"message": f"Change log {pk} has been rejected"})
            else:
                return Response({"message": "Invalid status provided. Available choices."})
        else:
            return Response({"message": "You do not have permission to update this change log"})

### Here User All the Log history showing based on user token ###
class AccessLogViewSet(viewsets.ViewSet):
    serializer_class = AccessLogSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        logs_data = AccessLog.objects.filter(user=request.user).order_by('-timestamp')
        serializer = AccessLogSerializer(logs_data, many=True)
        return Response(serializer.data)