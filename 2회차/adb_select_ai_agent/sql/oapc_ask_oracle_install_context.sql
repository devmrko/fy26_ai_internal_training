-- Ask Oracle SQLPlus import context
--
-- Run as the parsing schema user before executing the official Ask Oracle APEX
-- export SQL file.
--
-- Example:
--   sqlplus TRAIN05/"<PASSWORD>"@d8aukro81636mon0_low
--   @2회차/adb_select_ai_agent/sql/oapc_ask_oracle_install_context.sql
--   @/tmp/ADB-AskOracle-Chatbot-2026-03-04.sql

SET DEFINE OFF
SET SERVEROUTPUT ON SIZE UNLIMITED

BEGIN
  apex_application_install.set_workspace('OAPC_DEMO');
  apex_application_install.set_application_id(108);
  apex_application_install.set_application_alias('ASKORACLE');
  apex_application_install.set_application_name('Ask Oracle');
  apex_application_install.set_schema('TRAIN05');
  apex_application_install.set_auto_install_sup_obj(TRUE);

  DBMS_OUTPUT.PUT_LINE('Ask Oracle import context has been set.');
  DBMS_OUTPUT.PUT_LINE('Next: run @/tmp/ADB-AskOracle-Chatbot-2026-03-04.sql');
END;
/
