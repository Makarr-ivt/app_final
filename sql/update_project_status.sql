CREATE OR REPLACE FUNCTION public.update_project_status(
	p_project_id integer,
	p_manager_id integer,
	p_new_status project_status)
    RETURNS boolean
    LANGUAGE 'plpgsql'
AS $BODY$
BEGIN
    UPDATE projects
    SET status = p_new_status
    WHERE id = p_project_id AND manager_id = p_manager_id;
    RETURN FOUND;
END;
$BODY$;