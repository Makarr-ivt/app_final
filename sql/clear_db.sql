-- Отключаем внешние ключи на время очистки
SET session_replication_role = 'replica';

-- Очищаем таблицы
TRUNCATE TABLE tasks CASCADE;
TRUNCATE TABLE project_members CASCADE;
TRUNCATE TABLE projects CASCADE;
TRUNCATE TABLE users CASCADE;
TRUNCATE TABLE auth_group_permissions CASCADE;
TRUNCATE TABLE auth_group CASCADE;
TRUNCATE TABLE auth_permission CASCADE;

-- Сбрасываем счетчики
ALTER SEQUENCE tasks_id_seq RESTART WITH 1;
ALTER SEQUENCE project_members_id_seq RESTART WITH 1;
ALTER SEQUENCE projects_id_seq RESTART WITH 1;
ALTER SEQUENCE users_id_seq RESTART WITH 1;
ALTER SEQUENCE auth_group_id_seq RESTART WITH 1;
ALTER SEQUENCE auth_permission_id_seq RESTART WITH 1;

-- Включаем обратно внешние ключи
SET session_replication_role = 'origin';