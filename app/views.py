from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib import messages
from django.db import connection
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from .models import User
from .forms import ProfileEditForm, CustomPasswordChangeForm

# Create your views here.

def register_view(request):
    if request.method == 'POST':
        # Получаем данные из формы
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        role = request.POST.get('role')

        # Проверяем совпадение паролей
        if password != password_confirm:
            messages.error(request, 'Пароли не совпадают')
            return render(request, 'auth/register.html')

        # Проверяем, что email не занят
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE email = %s", [email])
            if cursor.fetchone() is not None:
                messages.error(request, 'Пользователь с таким email уже существует')
                return render(request, 'auth/register.html')

        # Хешируем пароль
        password_hash = make_password(password)

        # Регистрируем пользователя через SQL-функцию
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT register_user(%s, %s, %s, %s, %s)",
                [email, first_name, last_name, password_hash, role]
            )
            user_id = cursor.fetchone()[0]

        # Получаем созданного пользователя и выполняем вход
        user = User.objects.get(id=user_id)
        login(request, user)
        
        messages.success(request, 'Регистрация успешна!')
        return redirect('project_list')

    return render(request, 'auth/register.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Аутентифицируем пользователя
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Вы успешно вошли в систему')
            return redirect('project_list')
        else:
            messages.error(request, 'Неверный email или пароль')
            return render(request, 'auth/login.html')

    return render(request, 'auth/login.html')

def logout_view(request):
    logout(request)
    messages.info(request, 'Вы вышли из системы')
    return redirect('login')

@login_required
def project_list(request):
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    show_my = request.GET.get('show_my') == 'on'

    with connection.cursor() as cursor:
        base_query = """
            SELECT p.id, p.project_name, p.project_description, p.status, 
                   p.created_at, u.first_name, u.last_name
            FROM projects p
            JOIN users u ON p.manager_id = u.id
            WHERE 1=1
        """
        params = []

        if show_my:
            if request.user.role == 'manager':
                base_query += " AND p.manager_id = %s"
                params.append(request.user.id)
            else:
                base_query = """
                    SELECT p.id, p.project_name, p.project_description, p.status, 
                           p.created_at, u.first_name, u.last_name
                    FROM projects p
                    JOIN users u ON p.manager_id = u.id
                    JOIN project_members pm ON p.id = pm.project_id
                    WHERE pm.user_id = %s
                """
                params = [request.user.id]

        if search_query:
            base_query += " AND (CONCAT(p.id::text, ': ', p.project_name) ILIKE %s)"
            params.append(f'%{search_query}%')

        if status_filter:
            base_query += " AND p.status = %s"
            params.append(status_filter)

        base_query += " ORDER BY p.created_at DESC"
        
        cursor.execute(base_query, params)
        projects = cursor.fetchall()

    return render(request, 'projects/list.html', {
        'projects': projects,
        'search_query': search_query,
        'status_filter': status_filter,
        'show_my': show_my,
        'statuses': ['recruiting', 'in_progress', 'completed']
    })

@login_required
def project_detail(request, project_id):
    with connection.cursor() as cursor:
        # Получаем информацию о проекте
        cursor.execute("""
            SELECT p.id, p.project_name, p.project_description, p.status, 
                   p.created_at, u.first_name, u.last_name, u.id
            FROM projects p
            JOIN users u ON p.manager_id = u.id
            WHERE p.id = %s
        """, [project_id])
        project = cursor.fetchone()
        
        if not project:
            messages.error(request, 'Проект не найден')
            return redirect('project_list')

        # Получаем список участников проекта
        cursor.execute("""
            SELECT u.id, u.first_name, u.last_name, u.email,
                   COALESCE(COUNT(t.id) FILTER (WHERE t.status = 'completed'), 0) as completed_tasks
            FROM users u
            JOIN project_members pm ON u.id = pm.user_id
            LEFT JOIN tasks t ON t.worker_id = u.id 
                AND t.project_id = pm.project_id
            WHERE pm.project_id = %s
            GROUP BY u.id, u.first_name, u.last_name, u.email
            ORDER BY u.first_name, u.last_name
        """, [project_id])
        members = cursor.fetchall()

        # Получаем список задач проекта
        cursor.execute("""
            SELECT t.id, t.task_name, t.task_description, t.status, 
                   t.worker_id, u.first_name, u.last_name
            FROM tasks t
            LEFT JOIN users u ON t.worker_id = u.id
            WHERE t.project_id = %s
            ORDER BY 
                CASE t.status 
                    WHEN 'new' THEN 1
                    WHEN 'in_progress' THEN 2
                    WHEN 'completed' THEN 3
                END,
                t.created_at DESC
        """, [project_id])
        tasks = cursor.fetchall()

        # Проверяем, является ли текущий пользователь участником проекта
        cursor.execute("""
            SELECT EXISTS(
                SELECT 1 FROM project_members 
                WHERE project_id = %s AND user_id = %s
            )
        """, [project_id, request.user.id])
        is_member = cursor.fetchone()[0]

    return render(request, 'projects/detail.html', {
        'project': project,
        'members': members,
        'tasks': tasks,
        'is_member': is_member,
        'can_join': request.user.role == 'worker' and not is_member and project[3] == 'recruiting',
        'can_manage_members': request.user.id == project[7]  # project[7] это id менеджера
    })

@login_required
def my_projects(request):
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')

    with connection.cursor() as cursor:
        if request.user.role == 'manager':
            # Для менеджера показываем проекты, где он руководитель
            base_query = """
                SELECT p.id, p.project_name, p.project_description, p.status, 
                       p.created_at, u.first_name, u.last_name
                FROM projects p
                JOIN users u ON p.manager_id = u.id
                WHERE p.manager_id = %s
            """
            params = [request.user.id]
        else:
            # Для работника показываем проекты, где он участник
            base_query = """
                SELECT p.id, p.project_name, p.project_description, p.status, 
                       p.created_at, u.first_name, u.last_name
                FROM projects p
                JOIN users u ON p.manager_id = u.id
                JOIN project_members pm ON p.id = pm.project_id
                WHERE pm.user_id = %s
            """
            params = [request.user.id]

        if search_query:
            base_query += " AND (CONCAT(p.id::text, ': ', p.project_name) ILIKE %s)"
            params.append(f'%{search_query}%')

        if status_filter:
            base_query += " AND p.status = %s"
            params.append(status_filter)

        base_query += " ORDER BY p.created_at DESC"
        
        cursor.execute(base_query, params)
        projects = cursor.fetchall()

    return render(request, 'projects/list.html', {
        'projects': projects,
        'is_my_projects': True,
        'search_query': search_query,
        'status_filter': status_filter,
        'statuses': ['recruiting', 'in_progress', 'completed']
    })

@login_required
def create_project(request):
    if request.user.role != 'manager':
        messages.error(request, 'Только менеджеры могут создавать проекты')
        return redirect('project_list')

    if request.method == 'POST':
        project_name = request.POST.get('project_name')
        project_description = request.POST.get('project_description')

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO projects (manager_id, project_name, project_description, status)
                VALUES (%s, %s, %s, 'recruiting')
                RETURNING id
            """, [request.user.id, project_name, project_description])
            project_id = cursor.fetchone()[0]

        messages.success(request, 'Проект успешно создан')
        return redirect('project_detail', project_id=project_id)

    return render(request, 'projects/create.html')

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=request.user)
        if form.is_valid():
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE users 
                    SET first_name = %s, last_name = %s, email = %s
                    WHERE id = %s
                """, [
                    form.cleaned_data['first_name'],
                    form.cleaned_data['last_name'],
                    form.cleaned_data['email'],
                    request.user.id
                ])
            messages.success(request, 'Профиль успешно обновлен')
            return redirect('profile')
    else:
        form = ProfileEditForm(instance=request.user)
    
    return render(request, 'auth/edit_profile.html', {
        'form': form
    })

@login_required
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            # Сначала обновляем пароль в базе
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE users 
                    SET password = %s
                    WHERE id = %s
                """, [
                    make_password(form.cleaned_data['new_password1']),
                    request.user.id
                ])
            
            # Получаем обновленного пользователя
            user = User.objects.get(id=request.user.id)
            # Обновляем сессию
            update_session_auth_hash(request, user)
            
            messages.success(request, 'Пароль успешно изменен')
            return redirect('profile')
    else:
        form = CustomPasswordChangeForm(request.user)
    
    return render(request, 'auth/change_password.html', {
        'form': form
    })

@login_required
def join_project(request, project_id):
    if request.user.role != 'worker':
        messages.error(request, 'Только работники могут присоединяться к проектам')
        return redirect('project_detail', project_id=project_id)

    try:
        with connection.cursor() as cursor:
            cursor.execute("CALL join_project(%s, %s)", [project_id, request.user.id])
            messages.success(request, 'Вы успешно присоединились к проекту')
    except Exception as e:
        messages.error(request, str(e))

    return redirect('project_detail', project_id=project_id)

@login_required
def leave_project(request, project_id):
    if request.method == 'POST':
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "CALL leave_project(%s, %s)",
                    [project_id, request.user.id]
                )
                messages.success(request, 'Вы успешно покинули проект')
        except Exception as e:
            messages.error(request, str(e))

    return redirect('project_list')

@login_required
def remove_member(request, project_id, user_id):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            # Проверяем, что текущий пользователь является менеджером проекта
            cursor.execute("""
                SELECT EXISTS(
                    SELECT 1 FROM projects 
                    WHERE id = %s AND manager_id = %s
                )
            """, [project_id, request.user.id])
            is_manager = cursor.fetchone()[0]

            if not is_manager:
                messages.error(request, 'Только менеджер может удалять участников')
                return redirect('project_detail', project_id=project_id)

            # Проверяем, что удаляемый пользователь не является менеджером
            cursor.execute("""
                SELECT EXISTS(
                    SELECT 1 FROM projects 
                    WHERE id = %s AND manager_id = %s
                )
            """, [project_id, user_id])
            is_target_manager = cursor.fetchone()[0]

            if is_target_manager:
                messages.error(request, 'Нельзя удалить менеджера проекта')
                return redirect('project_detail', project_id=project_id)

            try:
                cursor.execute(
                    "CALL leave_project(%s, %s)",
                    [project_id, user_id]
                )
                messages.success(request, 'Участник успешно удален из проекта')
            except Exception as e:
                messages.error(request, str(e))

    return redirect('project_detail', project_id=project_id)

@login_required
def change_project_status(request, project_id):
    if request.method == 'POST':
        new_status = request.POST.get('status')
        
        if new_status not in ['recruiting', 'in_progress', 'completed']:
            messages.error(request, 'Некорректный статус проекта')
            return redirect('project_detail', project_id=project_id)

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "CALL update_project_status(%s, %s, %s)",
                    [project_id, request.user.id, new_status]
                )
                messages.success(request, 'Статус проекта успешно обновлен')
        except Exception as e:
            messages.error(request, str(e))
        
        return redirect('project_detail', project_id=project_id)
    
    return redirect('project_detail', project_id=project_id)

@login_required
def create_task(request, project_id):
    # Проверяем, является ли пользователь менеджером проекта
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT EXISTS(
                SELECT 1 FROM projects 
                WHERE id = %s AND manager_id = %s
            )
        """, [project_id, request.user.id])
        is_manager = cursor.fetchone()[0]

        if not is_manager:
            messages.error(request, 'Только менеджер проекта может создавать задачи')
            return redirect('project_detail', project_id=project_id)

        # Получаем список участников для формы
        cursor.execute("""
            SELECT u.id, u.first_name, u.last_name
            FROM users u
            JOIN project_members pm ON u.id = pm.user_id
            WHERE pm.project_id = %s
            ORDER BY u.first_name, u.last_name
        """, [project_id])
        members = cursor.fetchall()

        if request.method == 'POST':
            task_name = request.POST.get('task_name')
            task_description = request.POST.get('task_description')
            worker_id = request.POST.get('worker_id')

            # Создаем задачу через функцию БД
            try:
                cursor.execute(
                    "SELECT create_task(%s, %s, %s, %s, %s)",
                    [project_id, request.user.id, task_name, task_description, worker_id or None]
                )
                task_id = cursor.fetchone()[0]
                messages.success(request, 'Задача успешно создана')
            except Exception as e:
                messages.error(request, str(e))
            
            return redirect('project_detail', project_id=project_id)

    return render(request, 'projects/create_task.html', {
        'project_id': project_id,
        'members': members
    })

@login_required
def assign_task(request, task_id):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            try:
                cursor.execute(
                    "SELECT assign_task(%s, %s)",
                    [task_id, request.user.id]
                )
                if cursor.fetchone()[0]:
                    messages.success(request, 'Задача взята в работу')
            except Exception as e:
                messages.error(request, str(e))
            # Получаем project_id для редиректа
            cursor.execute(
                "SELECT project_id FROM tasks WHERE id = %s",
                [task_id]
            )
            project_id = cursor.fetchone()[0]
    return redirect('project_detail', project_id=project_id)

@login_required
def update_task_status(request, task_id):
    if request.method == 'POST':
        new_status = request.POST.get('status')
        
        if new_status not in ['new', 'in_progress', 'completed']:
            messages.error(request, 'Некорректный статус задачи')
            return redirect('project_detail', project_id=project_id)

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "CALL update_task_status(%s, %s, %s)",
                    [task_id, request.user.id, new_status]
                )
                messages.success(request, 'Статус задачи успешно обновлен')
        except Exception as e:
            messages.error(request, str(e))
            
        # Получаем project_id для редиректа
        with connection.cursor() as cursor:
            cursor.execute("SELECT project_id FROM tasks WHERE id = %s", [task_id])
            project_id = cursor.fetchone()[0]
            
        return redirect('project_detail', project_id=project_id)
    
    return redirect('project_list')

@login_required
def delete_task(request, task_id):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            # Получаем project_id для редиректа до удаления задачи
            cursor.execute(
                "SELECT project_id FROM tasks WHERE id = %s",
                [task_id]
            )
            result = cursor.fetchone()
            project_id = result[0] if result else None

            try:
                cursor.execute(
                    "CALL delete_task(%s, %s)",
                    [task_id, request.user.id]
                )
                messages.success(request, 'Задача успешно удалена')
            except Exception as e:
                messages.error(request, str(e))

            if not project_id:
                # Если задача уже удалена или не найдена, получаем project_id из реферера
                return redirect(request.META.get('HTTP_REFERER', 'project_list'))

    return redirect('project_detail', project_id=project_id)

@login_required
def profile_view(request):
    return render(request, 'auth/profile.html', {
        'user': request.user
    })
