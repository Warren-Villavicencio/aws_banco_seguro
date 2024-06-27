

# lambda_depositar_dinero.py

import json
import pymysql
import os

# RDS settings
rds_host = "database-1.cluster-c1w4j6m0z.us-west-2.rds.amazonaws.com"
db_name = os.environ["DATABASE_NAME"]
db_secret_arn = os.environ["DATABASE_SECRET"]

def depositar_dinero(event, context):
    data = json.loads(event["body"])
    numerodecuenta = data["numerodecuenta"]
    monto = data["monto"]

    try:
        conn = pymysql.connect(rds_host, user=db_name, passwd=db_secret_arn, db=db_name, connect_timeout=5)
        with conn.cursor() as cur:
            # Realiza la lógica para depositar dinero en la cuenta
            # Actualiza el saldo en la tabla cuentabancaria
            # ...
            pass
        conn.commit()
    except pymysql.MySQLError as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Error al procesar la solicitud"}),
        }

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Depósito exitoso"}),
    }
