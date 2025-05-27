CREATE OR REPLACE FUNCTION public.assign_task(
	p_task_id integer,
	p_worker_id integer)
    RETURNS boolean
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
AS $BODY$
DECLARE
    v_project_id INT;
BEGIN
    -- Получаем ID проекта
    SELECT project_id INTO v_project_id
    FROM tasks
    WHERE id = p_task_id;

    -- Проверяем, что задача существует
    IF v_project_id IS NULL THEN
        RAISE EXCEPTION 'Задача не найдена';
    END IF;

    -- Проверяем, что у задачи нет исполнителя
    IF EXISTS (
        SELECT 1 
        FROM tasks 
        WHERE id = p_task_id AND worker_id IS NOT NULL
    ) THEN
        RAISE EXCEPTION 'У задачи уже есть исполнитель';
    END IF;

    -- Проверяем, что работник является участником проекта
    IF NOT EXISTS (
        SELECT 1 
        FROM project_members 
        WHERE project_id = v_project_id AND user_id = p_worker_id
    ) THEN
        RAISE EXCEPTION 'Работник не является участником проекта';
    END IF;

    -- Назначаем исполнителя и меняем статус на "в работе"
    UPDATE tasks
    SET worker_id = p_worker_id,
        status = 'in_progress'::task_status
    WHERE id = p_task_id;

    RETURN TRUE;
END;
$BODY$;
