CREATE OR REPLACE FUNCTION public.join_project(
	p_project_id integer,
	p_user_id integer)
    RETURNS boolean
    LANGUAGE 'plpgsql'
AS $BODY$
BEGIN
    -- Проверяем, что проект существует и находится в статусе набора
    IF NOT EXISTS (
        SELECT 1 FROM projects 
        WHERE id = p_project_id AND status = 'recruiting'
    ) THEN
        RETURN FALSE;
    END IF;
    
    -- Проверяем, что пользователь является работником
    IF NOT EXISTS (
        SELECT 1 FROM users 
        WHERE id = p_user_id AND role = 'worker'
    ) THEN
        RETURN FALSE;
    END IF;
    
    -- Добавляем пользователя в проект
    INSERT INTO project_members (project_id, user_id)
    VALUES (p_project_id, p_user_id)
    ON CONFLICT DO NOTHING;
    
    RETURN TRUE;
END;
$BODY$;