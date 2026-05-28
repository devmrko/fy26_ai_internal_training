-- OAPC 3rd lab ADMIN preparation script
--
-- Run as ADMIN before the class.
-- Purpose:
--   1. Ensure TRAIN01-TRAIN30 users exist and have the baseline lab password.
--   2. Grant packages and metadata views required by Select AI and Select AI Agent.
--   3. Enable resource principal and Database Actions access for each TRAINxx user.
--
-- This script is intentionally ADMIN-only. Students do not run this file.

SET SERVEROUTPUT ON SIZE UNLIMITED

DECLARE
  l_password CONSTANT VARCHAR2(128) := 'Welcome#12345';

  PROCEDURE try_exec (
    p_sql      IN VARCHAR2,
    p_required IN BOOLEAN DEFAULT FALSE
  ) IS
  BEGIN
    EXECUTE IMMEDIATE p_sql;
  EXCEPTION
    WHEN OTHERS THEN
      IF p_required THEN
        RAISE;
      END IF;
      DBMS_OUTPUT.PUT_LINE('WARN: ' || SUBSTR(p_sql, 1, 120) || ' -> ' || SQLERRM);
  END;

  PROCEDURE ensure_user (p_user IN VARCHAR2) IS
    l_exists NUMBER;
  BEGIN
    SELECT COUNT(*)
    INTO   l_exists
    FROM   all_users
    WHERE  username = p_user;

    IF l_exists = 0 THEN
      try_exec('CREATE USER ' || p_user || ' IDENTIFIED BY "' || l_password || '"', TRUE);
      DBMS_OUTPUT.PUT_LINE('CREATED USER ' || p_user);
    ELSE
      try_exec('ALTER USER ' || p_user || ' IDENTIFIED BY "' || l_password || '" ACCOUNT UNLOCK');
      DBMS_OUTPUT.PUT_LINE('USER EXISTS ' || p_user);
    END IF;

    try_exec('GRANT CREATE SESSION TO ' || p_user);
    try_exec('GRANT CREATE TABLE TO ' || p_user);
    try_exec('GRANT CREATE VIEW TO ' || p_user);
    try_exec('GRANT CREATE PROCEDURE TO ' || p_user);
    try_exec('GRANT CREATE SEQUENCE TO ' || p_user);
    try_exec('GRANT UNLIMITED TABLESPACE TO ' || p_user);
    try_exec('GRANT DWROLE TO ' || p_user);

    try_exec('GRANT EXECUTE ON C##CLOUD$SERVICE.DBMS_CLOUD TO ' || p_user);
    try_exec('GRANT EXECUTE ON C##CLOUD$SERVICE.DBMS_CLOUD_AI TO ' || p_user);
    try_exec('GRANT EXECUTE ON C##CLOUD$SERVICE.DBMS_CLOUD_AI_AGENT TO ' || p_user);
    try_exec('GRANT EXECUTE ON DBMS_LOB TO ' || p_user);

    try_exec('GRANT SELECT ON DBA_AI_AGENT_TASKS TO ' || p_user);
    try_exec('GRANT SELECT ON DBA_AI_AGENT_TASK_ATTRIBUTES TO ' || p_user);
    try_exec('GRANT SELECT ON DBA_AI_AGENT_TOOLS TO ' || p_user);
    try_exec('GRANT SELECT ON DBA_AI_AGENT_TOOL_ATTRIBUTES TO ' || p_user);
    try_exec('GRANT SELECT ON DBA_AI_AGENT_TEAMS TO ' || p_user);
    try_exec('GRANT SELECT ON DBA_AI_AGENT_TEAM_ATTRIBUTES TO ' || p_user);

    try_exec('GRANT READ ON SYS.V_$MAPPED_SQL TO ' || p_user);
    try_exec('GRANT READ ON SYS.V_$SESSION TO ' || p_user);

    BEGIN
      DBMS_CLOUD_ADMIN.ENABLE_RESOURCE_PRINCIPAL(username => p_user);
      DBMS_OUTPUT.PUT_LINE('RESOURCE PRINCIPAL ENABLED ' || p_user);
    EXCEPTION
      WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('WARN: ENABLE_RESOURCE_PRINCIPAL ' || p_user || ' -> ' || SQLERRM);
    END;

    BEGIN
      ORDS_ADMIN.ENABLE_SCHEMA(
        p_enabled             => TRUE,
        p_schema              => p_user,
        p_url_mapping_type    => 'BASE_PATH',
        p_url_mapping_pattern => LOWER(p_user),
        p_auto_rest_auth      => NULL
      );
      COMMIT;
      DBMS_OUTPUT.PUT_LINE('ORDS ENABLED ' || p_user);
    EXCEPTION
      WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('WARN: ORDS ENABLE_SCHEMA ' || p_user || ' -> ' || SQLERRM);
    END;
  END;
BEGIN
  FOR i IN 1..30 LOOP
    ensure_user('TRAIN' || LPAD(i, 2, '0'));
  END LOOP;
END;
/

SELECT username, account_status
FROM   dba_users
WHERE  username LIKE 'TRAIN__'
ORDER  BY username;
