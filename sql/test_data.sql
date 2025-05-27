-- Создание пользователей
-- Менеджеры
SELECT register_user(
    'anna.petrova@example.com',
    'Анна',
    'Петрова',
    -- пароль: manager123
    'pbkdf2_sha256$1000000$Mrc8yLN1g2qcXd765jDgfZ$pfB2OjIJCNaYvk2FYIhldj/VB85EDlMxvgHqRUUsWCk=',
    'manager'::user_role
);

SELECT register_user(
    'ivan.sidorov@example.com',
    'Иван',
    'Сидоров',
    -- пароль: manager456
    'pbkdf2_sha256$1000000$i7S31LLTQSiBoHg4uCEYc1$Phl7wacfrhz1OWZm4UhkUWmjSFSjyFnxzd14L66cvSI=',
    'manager'::user_role
);

-- Исполнители
SELECT register_user(
    'maria.ivanova@example.com',
    'Мария',
    'Иванова',
    -- пароль: worker123
    'pbkdf2_sha256$1000000$QgEZtgWEu8yG1n6bTnrhoB$xG2TDi/W+tWHkZfUF9GcG0VEpMcAIkdrGMdrEq5wEwE=',
    'worker'::user_role
);

SELECT register_user(
    'alexey.smirnov@example.com',
    'Алексей',
    'Смирнов',
    -- пароль: worker456
    'pbkdf2_sha256$1000000$yZa2JxGr4O4exiYSr9eBvv$UBlTpaXdpMNXWni1t8nhbyD4S2OBjXGhsE6KAlNQqF8=',
    'worker'::user_role
);

SELECT register_user(
    'elena.kozlova@example.com',
    'Елена',
    'Козлова',
    -- пароль: worker789
    'pbkdf2_sha256$1000000$yxPUlP2AgFAgHbiCnAv5ya$voehNVLolKGlxFdXqUZTbd0BhB+AqGYhn2ahUgXN4RI=',
    'worker'::user_role
);

-- Создание проектов
DO $$
DECLARE
    anna_id INTEGER;
    ivan_id INTEGER;
    maria_id INTEGER;
    alexey_id INTEGER;
    elena_id INTEGER;
    project1_id INTEGER;
    project2_id INTEGER;
    project3_id INTEGER;
    task_id INTEGER;
BEGIN
    -- Получаем ID пользователей
    SELECT id INTO anna_id FROM users WHERE email = 'anna.petrova@example.com';
    SELECT id INTO ivan_id FROM users WHERE email = 'ivan.sidorov@example.com';
    SELECT id INTO maria_id FROM users WHERE email = 'maria.ivanova@example.com';
    SELECT id INTO alexey_id FROM users WHERE email = 'alexey.smirnov@example.com';
    SELECT id INTO elena_id FROM users WHERE email = 'elena.kozlova@example.com';

    -- Создаем проекты
    SELECT create_project(
        anna_id,
        'Разработка веб-сайта компании',
        'Создание современного корпоративного сайта с адаптивным дизайном'
    ) INTO project1_id;

    SELECT create_project(
        ivan_id,
        'Мобильное приложение для фитнеса',
        'Разработка приложения для отслеживания тренировок и питания'
    ) INTO project2_id;

    SELECT create_project(
        anna_id,
        'Система учета клиентов',
        'Внутренняя CRM система для работы с клиентами'
    ) INTO project3_id;

    -- Добавляем участников в проекты
    PERFORM join_project(project2_id, maria_id);
    PERFORM join_project(project2_id, alexey_id);
    PERFORM join_project(project3_id, elena_id);
    PERFORM join_project(project3_id, maria_id);

    -- Создаем задачи для первого проекта (пока без исполнителей)
    SELECT create_task(
        project1_id,
        anna_id,
        'Разработка главной страницы',
        'Создание адаптивной главной страницы с современным дизайном'
    ) INTO task_id;

    SELECT create_task(
        project1_id,
        anna_id,
        'Настройка системы авторизации',
        'Реализация регистрации и входа пользователей'
    ) INTO task_id;

    -- Создаем и назначаем задачи для второго проекта
    SELECT create_task(
        project2_id,
        ivan_id,
        'Создание UI прототипа',
        'Разработка интерфейса основных экранов приложения',
        maria_id
    ) INTO task_id;
    PERFORM update_task_status(task_id, maria_id, 'completed'::task_status);

    SELECT create_task(
        project2_id,
        ivan_id,
        'Разработка модуля статистики',
        'Создание системы отображения прогресса пользователя',
        alexey_id
    ) INTO task_id;
    PERFORM update_task_status(task_id, alexey_id, 'in_progress'::task_status);

    SELECT create_task(
        project2_id,
        ivan_id,
        'Интеграция с фитнес-трекерами',
        'Добавление поддержки популярных фитнес-браслетов'
    ) INTO task_id;

    -- Создаем и назначаем задачи для третьего проекта
    SELECT create_task(
        project3_id,
        anna_id,
        'Импорт базы клиентов',
        'Перенос данных из старой системы',
        elena_id
    ) INTO task_id;
    PERFORM update_task_status(task_id, elena_id, 'completed'::task_status);

    SELECT create_task(
        project3_id,
        anna_id,
        'Разработка отчетов',
        'Создание системы формирования аналитических отчетов',
        maria_id
    ) INTO task_id;
    PERFORM update_task_status(task_id, maria_id, 'completed'::task_status);

    -- Обновляем статусы проектов
    PERFORM update_project_status(project2_id, ivan_id, 'in_progress'::project_status);
    PERFORM update_project_status(project3_id, anna_id, 'completed'::project_status);
END $$; 