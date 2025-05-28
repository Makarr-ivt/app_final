CREATE OR REPLACE PROCEDURE public.leave_project(
	p_project_id integer,
	p_user_id integer)
    LANGUAGE 'plpgsql'
AS $BODY$
BEGIN
    -- Проверяем, что пользователь является участником проекта
    IF NOT EXISTS (
        SELECT 1 FROM project_members
        WHERE project_id = p_project_id AND user_id = p_user_id
    ) THEN
        RAISE EXCEPTION 'Пользователь не является участником проекта';
    END IF;

    -- Сначала освобождаем все незавершенные задачи пользователя
    UPDATE tasks
    SET worker_id = NULL,
        status = 'new'::task_status
    WHERE project_id = p_project_id 
    AND worker_id = p_user_id 
    AND status != 'completed'::task_status;

    -- Затем удаляем пользователя из проекта
    DELETE FROM project_members
    WHERE project_id = p_project_id AND user_id = p_user_id;
END;
$BODY$;