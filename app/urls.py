from django.urls import path
from . import views

urlpatterns = [
    # Аутентификация
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    
    # Профиль пользователя
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/password/', views.change_password, name='change_password'),
    
    # Проекты
    path('', views.project_list, name='project_list'),
    path('projects/', views.project_list, name='project_list'),
    path('projects/create/', views.create_project, name='create_project'),
    path('projects/<int:project_id>/', views.project_detail, name='project_detail'),
    path('projects/<int:project_id>/change-status/', views.change_project_status, name='change_project_status'),
    
    # Задачи
    path('projects/<int:project_id>/tasks/create/', views.create_task, name='create_task'),
    path('tasks/<int:task_id>/assign/', views.assign_task, name='assign_task'),
    path('tasks/<int:task_id>/update-status/', views.update_task_status, name='update_task_status'),
    path('tasks/<int:task_id>/delete/', views.delete_task, name='delete_task'),
    
    # Участники проекта
    path('projects/<int:project_id>/join/', views.join_project, name='join_project'),
    path('projects/<int:project_id>/leave/', views.leave_project, name='leave_project'),
    path('projects/<int:project_id>/members/<int:user_id>/remove/', views.remove_member, name='remove_member'),
] 