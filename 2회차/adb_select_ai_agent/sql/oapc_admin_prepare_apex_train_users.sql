-- Prepare OAPC_DEMO APEX workspace for TRAIN01-TRAIN30.
--
-- Run as ADMIN or an APEX instance admin user.
--
-- Required SQL*Plus variables:
--   APEX_WORKSPACE       default OAPC_DEMO
--   TRAIN_PASSWORD       APEX runtime password for TRAINxx users

SET DEFINE ON
SET SERVEROUTPUT ON SIZE UNLIMITED
SET PAGESIZE 200
SET LINESIZE 240

DEFINE APEX_WORKSPACE = "OAPC_DEMO"

DECLARE
  l_workspace VARCHAR2(128) := UPPER('&&APEX_WORKSPACE');
  l_schema    VARCHAR2(30);
  l_count     NUMBER;
  l_user_id   NUMBER;
  l_sgid      NUMBER;
BEGIN
  l_sgid := APEX_UTIL.FIND_SECURITY_GROUP_ID(p_workspace => l_workspace);
  APEX_UTIL.SET_SECURITY_GROUP_ID(l_sgid);

  FOR i IN 1..30 LOOP
    l_schema := 'TRAIN' || LPAD(i, 2, '0');

    SELECT COUNT(*)
    INTO   l_count
    FROM   apex_workspace_schemas
    WHERE  workspace_name = l_workspace
    AND    schema = l_schema;

    IF l_count = 0 THEN
      APEX_INSTANCE_ADMIN.ADD_SCHEMA(
        p_workspace             => l_workspace,
        p_schema                => l_schema,
        p_grant_apex_privileges => TRUE
      );
      DBMS_OUTPUT.PUT_LINE('ADDED WORKSPACE SCHEMA ' || l_schema);
    ELSE
      DBMS_OUTPUT.PUT_LINE('SKIP  WORKSPACE SCHEMA ' || l_schema);
    END IF;

    l_user_id := APEX_UTIL.GET_USER_ID(l_schema);

    IF l_user_id IS NULL OR l_user_id = 0 THEN
      APEX_UTIL.CREATE_USER(
        p_user_name                    => l_schema,
        p_first_name                   => 'OAPC',
        p_last_name                    => l_schema,
        p_email_address                => LOWER(l_schema) || '@example.com',
        p_web_password                 => '&&TRAIN_PASSWORD',
        p_developer_privs              => NULL,
        p_default_schema               => l_schema,
        p_allow_access_to_schemas      => l_schema,
        p_change_password_on_first_use => 'N',
        p_account_locked               => 'N',
        p_allow_app_building_yn        => 'N',
        p_allow_sql_workshop_yn        => 'N',
        p_allow_websheet_dev_yn        => 'N',
        p_allow_team_development_yn    => 'N'
      );
      DBMS_OUTPUT.PUT_LINE('CREATED APEX USER ' || l_schema);
    ELSE
      APEX_UTIL.EDIT_USER(
        p_user_id                      => l_user_id,
        p_user_name                    => l_schema,
        p_new_password                 => '&&TRAIN_PASSWORD',
        p_email_address                => LOWER(l_schema) || '@example.com',
        p_allow_access_to_schemas      => l_schema,
        p_default_schema               => l_schema,
        p_account_locked               => 'N',
        p_change_password_on_first_use => 'N',
        p_first_password_use_occurred  => 'Y'
      );
      APEX_UTIL.UNLOCK_ACCOUNT(p_user_name => l_schema);
      DBMS_OUTPUT.PUT_LINE('UPDATED APEX USER ' || l_schema);
    END IF;
  END LOOP;

  COMMIT;
END;
/

PROMPT === Workspace Schemas ===
SELECT workspace_name, schema, applications
FROM apex_workspace_schemas
WHERE workspace_name = UPPER('&&APEX_WORKSPACE')
ORDER BY schema;

PROMPT === APEX Users ===
SELECT workspace_name, user_name, account_locked
FROM apex_workspace_apex_users
WHERE workspace_name = UPPER('&&APEX_WORKSPACE')
AND user_name LIKE 'TRAIN%'
ORDER BY user_name;
