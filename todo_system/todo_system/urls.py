from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api import views
#Create router Object
router = DefaultRouter()

router.register('todoapi', views.TodoViewSet, basename='todoapi')
router.register('todo-sharing', views.TodoSharingViewSet, basename='todo-sharing')
router.register('change-share-todo', views.ChangeSharedTodoViewSet, basename='change-share-todo')
router.register('owner-todo-change-logs', views.OwnerTodoChangeLogViewSet, basename='owner-todo-change-logs')
router.register('approve-reject-shared-todo', views.ApproveChangeLogViewSet, basename='approve-reject-change-logs')
router.register('user-access-log', views.AccessLogViewSet, basename='user-access-log')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('authentication/', include('api.urls')),
    path('', include(router.urls)),
]