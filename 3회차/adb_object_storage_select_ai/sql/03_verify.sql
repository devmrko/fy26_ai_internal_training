-- Run as TRAINING. Adjust metric column names only if your training ORC contract differs.
WHENEVER SQLERROR EXIT SQL.SQLCODE
SET SERVEROUTPUT ON

DEFINE business_date = '&1'

SELECT object_name, object_type, status
  FROM user_objects
 WHERE object_name IN (
   'GAME_USER_MST_EXT','GAME_BIZ_USER_TXN_EXT',
   'GAME_USER_MST','GAME_BIZ_USER_TXN'
 )
 ORDER BY object_name;

SELECT table_name, column_name, data_type
  FROM user_tab_columns
 WHERE table_name IN (
   'GAME_USER_MST_EXT','GAME_BIZ_USER_TXN_EXT',
   'GAME_USER_MST','GAME_BIZ_USER_TXN'
 )
   AND column_name = 'BASE_DT'
 ORDER BY table_name;

-- Physical Hive partition comparison uses VARCHAR2.
SELECT COUNT(*) AS USER_SAMPLE_ROWS
  FROM (
    SELECT 1 FROM GAME_USER_MST_EXT
     WHERE BASE_DT = '&&business_date'
     FETCH FIRST 1 ROW ONLY
  );

-- Consumer contract comparison uses DATE.
SELECT COUNT(DISTINCT u.GUID) AS STANDARD_AU_COUNT
  FROM GAME_USER_MST u
 WHERE u.BASE_DT = TO_DATE('&&business_date', 'YYYY-MM-DD')
   AND u.AU_FLAG = 1
   AND u.EXPT_USER_YN = 'N';

SELECT COUNT(DISTINCT b.GUID) AS BUSINESS_AU_COUNT
  FROM GAME_BIZ_USER_TXN b
 WHERE b.BASE_DT = TO_DATE('&&business_date', 'YYYY-MM-DD')
   AND b.BIZ_AU_FLAG = '1'
   AND b.EXPT_USER_YN = 'N';

UNDEFINE business_date
EXIT SUCCESS
