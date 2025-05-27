CREATE OR REPLACE FUNCTION public.create_task(
	p_project_id integer,
	p_manager_id integer,
	p_task_name character varying,
	p_task_description text DEFAULT NULL::text,
	p_worker_id integer DEFAULT NULL::integer)
    RETURNS integer
    LANGUAGE 'plpgsql'
AS $BODY$
DECLARE
    v_task_id INT;
BEGIN
    -- Проверяем, является ли пользователь менеджером проекта
    IF NOT EXISTS (
        SELECT 1 
        FROM projects 
        WHERE id = p_project_id AND manager_id = p_manager_id
    ) THEN
        RAISE EXCEPTION 'Только менеджер проекта может создавать задачи';
    END IF;

    -- Если указан работник, проверяем, является ли он участником проекта
    IF p_worker_id IS NOT NULL AND NOT EXISTS (
        SELECT 1 
        FROM project_members 
        WHERE project_id = p_project_id AND user_id = p_worker_id
    ) THEN
        RAISE EXCEPTION 'Указанный работник не является участником проекта';
    END IF;

    -- Создаем задачу
    INSERT INTO tasks (
        project_id,
        worker_id,
        task_name,
        task_description,
        status,
        created_at
    ) VALUES (
        p_project_id,
        p_worker_id,
        p_task_name,
        p_task_description,
        'new'::task_status,
        NOW()
    ) RETURNING id INTO v_task_id;

    RETURN v_task_id;
END;
$BODY$;

CREATE OR REPLACE FUNCTION public.create_task(
	p_project_id integer,
	p_task_name character varying,
	p_task_description text,
	p_worker_id integer DEFAULT NULL::integer)
    RETURNS integer
    LANGUAGE 'plpgsql'
AS $BODY$
DECLARE
    new_task_id INTEGER;
BEGIN
    INSERT INTO tasks (project_id, worker_id, task_name, task_description)
    VALUES (p_project_id, p_worker_id, p_task_name, p_task_description)
    RETURNING id INTO new_task_id;
    RETURN new_task_id;
END;
$BODY$;