#!/usr/bin/env python3
"""Create DBMS_VECTOR credentials for OAPC TRAINxx users.

The script reads OCI API key information from ~/.oci/config DEFAULT and creates
GENAI_VECTOR_CRED in each TRAINxx schema. The private key is sent only through
SQLPlus stdin and is not written to repository files.
"""

from __future__ import annotations

import argparse
import configparser
import json
import os
import pathlib
import subprocess
import sys


def parse_users(value: str) -> list[str]:
    result: list[str] = []
    for part in value.split(","):
        part = part.strip().upper()
        if not part:
            continue
        if "-" in part:
            start, end = part.split("-", 1)
            prefix = "".join(ch for ch in start if not ch.isdigit())
            start_num = int("".join(ch for ch in start if ch.isdigit()))
            end_num = int("".join(ch for ch in end if ch.isdigit()))
            width = max(
                len("".join(ch for ch in start if ch.isdigit())),
                len("".join(ch for ch in end if ch.isdigit())),
            )
            for i in range(start_num, end_num + 1):
                result.append(f"{prefix}{i:0{width}d}")
        else:
            result.append(part)
    return result


def q_literal(value: str) -> str:
    for open_delim, close_delim in [("[", "]"), ("{", "}"), ("(", ")"), ("<", ">")]:
        token = close_delim + "'"
        if token not in value:
            return f"q'{open_delim}{value}{close_delim}'"
    raise ValueError("Unable to quote credential JSON safely")


def load_oci_params(profile: str, compartment_ocid: str | None) -> tuple[dict[str, str], str]:
    cfg = configparser.ConfigParser()
    config_path = pathlib.Path.home() / ".oci" / "config"
    read_files = cfg.read(config_path)
    if not read_files:
        raise FileNotFoundError(f"OCI config not found: {config_path}")
    if profile not in cfg:
        raise KeyError(f"OCI profile not found: {profile}")

    section = cfg[profile]
    key_file = pathlib.Path(section["key_file"]).expanduser()
    private_key = key_file.read_text()
    tenancy_ocid = section["tenancy"]

    params = {
        "user_ocid": section["user"],
        "tenancy_ocid": tenancy_ocid,
        "compartment_ocid": compartment_ocid or tenancy_ocid,
        "fingerprint": section["fingerprint"],
        "private_key": private_key,
    }
    return params, section.get("region", "us-ashburn-1")


def build_sql(credential_name: str, params: dict[str, str], test_embedding: bool, region: str) -> str:
    params_json = json.dumps(params)
    embedding_params = {
        "provider": "ocigenai",
        "credential_name": credential_name,
        "url": f"https://inference.generativeai.{region}.oci.oraclecloud.com/20231130/actions/embedText",
        "model": "cohere.embed-v4.0",
    }
    lines = [
        "SET SERVEROUTPUT ON SIZE UNLIMITED",
        "WHENEVER SQLERROR EXIT SQL.SQLCODE",
        "DECLARE",
        "  v VECTOR;",
        "BEGIN",
        f"  BEGIN DBMS_VECTOR.DROP_CREDENTIAL('{credential_name}'); EXCEPTION WHEN OTHERS THEN NULL; END;",
        "  DBMS_VECTOR.CREATE_CREDENTIAL(",
        f"    credential_name => '{credential_name}',",
        f"    params          => JSON({q_literal(params_json)})",
        "  );",
    ]
    if test_embedding:
        lines.extend(
            [
                "  v := DBMS_VECTOR.UTL_TO_EMBEDDING(",
                "    'OAPC vector credential smoke test',",
                f"    JSON({q_literal(json.dumps(embedding_params))})",
                "  );",
                "  DBMS_OUTPUT.PUT_LINE('credential=OK dim=' || VECTOR_DIMENSION_COUNT(v));",
            ]
        )
    else:
        lines.append("  DBMS_OUTPUT.PUT_LINE('credential=OK');")
    lines.extend(["END;", "/", "EXIT"])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--oci-profile", default="DEFAULT")
    parser.add_argument("--compartment-ocid", default=None)
    parser.add_argument("--users", default="TRAIN01-TRAIN30")
    parser.add_argument("--connect", default=os.environ.get("ADB_CONNECT", "d8aukro81636mon0_low"))
    parser.add_argument("--password", default=os.environ.get("OAPC_TRAIN_PASSWORD", "Welcome#12345"))
    parser.add_argument("--credential-name", default="GENAI_VECTOR_CRED")
    parser.add_argument("--sqlplus-bin", default=os.environ.get("SQLPLUS_BIN", "sqlplus"))
    parser.add_argument("--test-embedding", action="store_true")
    args = parser.parse_args()

    params, region = load_oci_params(args.oci_profile, args.compartment_ocid)
    users = parse_users(args.users)
    sql = build_sql(args.credential_name, params, args.test_embedding, region)

    failed: list[str] = []
    for user in users:
        connect_string = f'{user}/"{args.password}"@{args.connect}'
        proc = subprocess.run(
            [args.sqlplus_bin, "-s", connect_string],
            input=sql,
            text=True,
            capture_output=True,
            check=False,
        )
        if proc.returncode == 0 and "credential=OK" in proc.stdout:
            print(f"OK {user}")
        else:
            failed.append(user)
            print(f"FAIL {user}", file=sys.stderr)
            if proc.stdout:
                print(proc.stdout, file=sys.stderr)
            if proc.stderr:
                print(proc.stderr, file=sys.stderr)

    if failed:
        print("FAILED=" + ",".join(failed), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
