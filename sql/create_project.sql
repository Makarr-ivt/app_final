CREATE OR REPLACE FUNCTION public.create_project(
	p_manager_id integer,
	p_project_name character varying,
	p_project_description text)
    RETURNS integer
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
AS $BODY$
DECLARE
    new_project_id INTEGER;
BEGIN
    INSERT INTO projects (manager_id, project_name, project_description)
    VALUES (p_manager_id, p_project_name, p_project_description)
    RETURNING id INTO new_project_id;
    RETURN new_project_id;
END;
$BODY$;
