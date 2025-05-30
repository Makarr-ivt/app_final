CREATE OR REPLACE PROCEDURE public.update_task_status(
	p_task_id integer,
	p_worker_id integer,
	p_new_status task_status)
    LANGUAGE 'plpgsql'
AS $BODY$
BEGIN
    -- Проверяем, что работник является исполнителем задачи
    IF NOT EXISTS (
        SELECT 1 
        FROM tasks 
        WHERE id = p_task_id AND worker_id = p_worker_id
    ) THEN
        RAISE EXCEPTION 'Только исполнитель может изменять статус задачи';
    END IF;

    -- Обновляем статус
    UPDATE tasks
    SET status = p_new_status
    WHERE id = p_task_id;
END;
$BODY$;