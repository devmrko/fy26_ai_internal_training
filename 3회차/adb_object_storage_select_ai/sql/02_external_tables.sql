-- Run as TRAINING after Resource Principal can GET both exact ORC objects.
-- Args: object URI root, user ORC relative path, business ORC relative path.
WHENEVER SQLERROR EXIT SQL.SQLCODE
SET SERVEROUTPUT ON VERIFY OFF

DEFINE object_uri_root = '&1'
DEFINE user_orc_object = '&2'
DEFINE biz_orc_object = '&3'

DECLARE
  c_root CONSTANT VARCHAR2(2000) := RTRIM('&&object_uri_root', '/') || '/';

  PROCEDURE drop_external_if_exists(p_table VARCHAR2) IS
  BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE ' || DBMS_ASSERT.ENQUOTE_NAME(UPPER(p_table), FALSE);
  EXCEPTION
    WHEN OTHERS THEN
      IF SQLCODE != -942 THEN RAISE; END IF;
  END;

  PROCEDURE create_orc(p_table VARCHAR2, p_object VARCHAR2) IS
  BEGIN
    drop_external_if_exists(p_table);
    DBMS_CLOUD.CREATE_EXTERNAL_TABLE(
      table_name      => UPPER(p_table),
      credential_name => 'OCI$RESOURCE_PRINCIPAL',
      file_uri_list   => c_root || p_object,
      format          => JSON_OBJECT(
        'type' VALUE 'orc',
        'schema' VALUE 'first',
        'implicit_partition_config' VALUE JSON_OBJECT(
          'partition_type' VALUE 'hive',
          'strict_column_order' VALUE TRUE,
          'partition_columns' VALUE JSON_ARRAY('base_dt')
        )
      )
    );
    DBMS_OUTPUT.PUT_LINE('EXTERNAL_CREATED=' || UPPER(p_table));
  END;
BEGIN
  create_orc('GAME_USER_MST_EXT', '&&user_orc_object');
  create_orc('GAME_BIZ_USER_TXN_EXT', '&&biz_orc_object');
END;
/

-- Build stable consumer views from discovered metadata. BASE_DT is the only
-- physical Hive partition type normalized here; all other columns are preserved.
DECLARE
  PROCEDURE create_consumer_view(p_view VARCHAR2, p_external VARCHAR2) IS
    l_columns VARCHAR2(32767);
  BEGIN
    SELECT LISTAGG(
             CASE
               WHEN column_name = 'BASE_DT' THEN
                 'TO_DATE("BASE_DT", ''YYYY-MM-DD'') AS "BASE_DT"'
               ELSE DBMS_ASSERT.ENQUOTE_NAME(column_name, FALSE)
             END,
             ','
           ) WITHIN GROUP (ORDER BY column_id)
      INTO l_columns
      FROM user_tab_columns
     WHERE table_name = UPPER(p_external);

    IF l_columns IS NULL THEN
      RAISE_APPLICATION_ERROR(-20001, 'External metadata missing: ' || p_external);
    END IF;

    EXECUTE IMMEDIATE
      'CREATE OR REPLACE VIEW ' || DBMS_ASSERT.ENQUOTE_NAME(UPPER(p_view), FALSE) ||
      ' AS SELECT ' || l_columns || ' FROM ' ||
      DBMS_ASSERT.ENQUOTE_NAME(UPPER(p_external), FALSE);
  END;
BEGIN
  create_consumer_view('GAME_USER_MST', 'GAME_USER_MST_EXT');
  create_consumer_view('GAME_BIZ_USER_TXN', 'GAME_BIZ_USER_TXN_EXT');
END;
/

UNDEFINE object_uri_root
UNDEFINE user_orc_object
UNDEFINE biz_orc_object
EXIT SUCCESS
