CREATE TYPE user_role AS ENUM ('worker', 'manager');
CREATE TYPE project_status AS ENUM ('recruiting', 'in_progress', 'completed');
CREATE TYPE task_status AS ENUM ('new', 'in_progress', 'completed');