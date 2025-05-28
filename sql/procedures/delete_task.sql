CREATE OR REPLACE PROCEDURE public.delete_task(
	p_task_id integer,
	p_manager_id integer)
    LANGUAGE 'plpgsql'
AS $BODY$
BEGIN
    -- Проверяем, что задача существует и принадлежит проекту менеджера
    IF NOT EXISTS (
        SELECT 1 
        FROM tasks t
        JOIN projects p ON t.project_id = p.id
        WHERE t.id = p_task_id 
        AND p.manager_id = p_manager_id
    ) THEN
        RAISE EXCEPTION 'Задача не найдена или у вас нет прав для её удаления';
    END IF;

    -- Проверяем, что у задачи нет исполнителя
    IF EXISTS (
        SELECT 1 
        FROM tasks 
        WHERE id = p_task_id AND worker_id IS NOT NULL
    ) THEN
        RAISE EXCEPTION 'Нельзя удалить задачу, у которой есть исполнитель';
    END IF;

    -- Удаляем задачу
    DELETE FROM tasks WHERE id = p_task_id;
END;
$BODY$;