CREATE OR REPLACE FUNCTION public.leave_project(
	p_project_id integer,
	p_user_id integer)
    RETURNS boolean
    LANGUAGE 'plpgsql'
AS $BODY$
BEGIN
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
    
    RETURN FOUND;
END;
$BODY$;