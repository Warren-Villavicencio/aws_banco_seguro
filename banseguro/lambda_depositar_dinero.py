import json
import boto3
import os

from fastapi import FastAPI, Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base, Ingreso, DepositoBase
from db import get_db, Session


URL_DATABASE = os.environ["DATABASE_URL"]


engine = create_engine(URL_DATABASE)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base.metadata.create_all(engine)


db_dependency = Depends(get_db)


app = FastAPI()

@app.post("/depositar/", status_code=200)
async def depositar_dinero(deposito: DepositoBase, db: Session = db_dependency):
  
    cuenta = db.query(Ingreso).filter(Ingreso.numerodecuenta == deposito.numerodecuenta).first()

    if not cuenta:
        raise Exception("Cuenta no encontrada")

    
    cuenta.saldo += deposito.monto
    db.commit()


    send_email(cuenta, deposito)

    
    return {"mensaje": "Depósito realizado exitosamente", "saldo_actual": cuenta.saldo}


def send_email(cuenta, deposito):
    
    pass

# Empaquetar la aplicación FastAPI en un handler de Lambda
def lambda_handler(event, context):
    # Cargar el cuerpo de la solicitud JSON
    body = json.loads(event["body"])

    # Convertir el cuerpo en un objeto DepositoBase
    deposito = DepositoBase(**body)

    # Invocar la función `depositar_dinero`
    try:
        response = depositar_dinero(deposito)
        return {
            "statusCode": 200,
            "body": json.dumps(response),
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
        }

# Definir la variable de entorno para la URL de la base de datos
lambda_client = boto3.client("lambda")
lambda_client.update_function_configuration(
    FunctionName="banseguro-depositar",
    EnvironmentVariables={
        "DATABASE_URL": URL_DATABASE,
    },
)
