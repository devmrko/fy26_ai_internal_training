-- Run as TRAINING after an approved OCI AI credential is registered.
-- Args: compartment, credential, profile, model, region, provider endpoint.
WHENEVER SQLERROR EXIT SQL.SQLCODE
SET SERVEROUTPUT ON VERIFY OFF

DEFINE ai_compartment = '&1'
DEFINE ai_credential = '&2'
DEFINE ai_profile = '&3'
DEFINE ai_model = '&4'
DEFINE ai_region = '&5'
DEFINE provider_endpoint = '&6'

DECLARE
  l_count PLS_INTEGER;
  l_attributes CLOB;
BEGIN
  SELECT COUNT(*) INTO l_count
    FROM user_cloud_ai_profiles
   WHERE profile_name = UPPER('&&ai_profile');

  IF l_count > 0 THEN
    DBMS_CLOUD_AI.DROP_PROFILE(profile_name => UPPER('&&ai_profile'), force => TRUE);
  END IF;

  SELECT JSON_OBJECT(
           'provider' VALUE 'oci',
           'credential_name' VALUE '&&ai_credential',
           'model' VALUE '&&ai_model',
           'region' VALUE '&&ai_region',
           'provider_endpoint' VALUE '&&provider_endpoint',
           'oci_compartment_id' VALUE '&&ai_compartment',
           'object_list' VALUE JSON_ARRAY(
             JSON_OBJECT('owner' VALUE 'TRAINING', 'name' VALUE 'GAME_USER_MST'),
             JSON_OBJECT('owner' VALUE 'TRAINING', 'name' VALUE 'GAME_BIZ_USER_TXN')
           )
           RETURNING CLOB
         ) INTO l_attributes
    FROM dual;

  DBMS_CLOUD_AI.CREATE_PROFILE(
    profile_name => UPPER('&&ai_profile'),
    attributes   => l_attributes,
    description  => 'Training read-only Select AI profile'
  );
END;
/

SELECT profile_name, status, description
  FROM user_cloud_ai_profiles
 WHERE profile_name = UPPER('&&ai_profile');

UNDEFINE ai_compartment
UNDEFINE ai_credential
UNDEFINE ai_profile
UNDEFINE ai_model
UNDEFINE ai_region
UNDEFINE provider_endpoint
EXIT SUCCESS
