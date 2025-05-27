CREATE OR REPLACE FUNCTION public.register_user(
	p_email character varying,
	p_first_name character varying,
	p_last_name character varying,
	p_password_hash character varying,
	p_role user_role)
    RETURNS integer
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
AS $BODY$
DECLARE
    new_user_id INTEGER;
BEGIN
    INSERT INTO users (email, first_name, last_name, password, role)
    VALUES (p_email, p_first_name, p_last_name, p_password_hash, p_role)
    RETURNING id INTO new_user_id;
    RETURN new_user_id;
END;
$BODY$;