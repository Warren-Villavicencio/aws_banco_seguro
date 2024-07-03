import json
import boto3
import os

from fastapi import FastAPI, Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base, Ingreso, DepositoBase
from db import get_db, Session

# URL de la base de datos
URL_DATABASE = os.environ["DATABASE_URL"]

# Crear motor de base de datos
engine = create_engine(URL_DATABASE)

# Crear sesión local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Inicializar base de datos
Base.metadata.create_all(engine)

# Dependencia para obtener la sesión de la base de datos
db_dependency = Depends(get_db)

# Crear aplicación FastAPI
app = FastAPI()

# Función para depositar dinero
@app.post("/depositar/", status_code=200)
async def depositar_dinero(deposito: DepositoBase, db: Session = db_dependency):
    # Buscar cuenta por número de cuenta
    cuenta = db.query(Ingreso).filter(Ingreso.numerodecuenta == deposito.numerodecuenta).first()

    if not cuenta:
        raise Exception("Cuenta no encontrada")

    # Actualizar saldo y guardar en la base de datos
    cuenta.saldo += deposito.monto
    db.commit()

    # Enviar correo electrónico de notificación
    send_email(cuenta, deposito)

    # Devolver respuesta con mensaje y saldo actual
    return {"mensaje": "Depósito realizado exitosamente", "saldo_actual": cuenta.saldo}

# Función para enviar correo electrónico (implementar la lógica)
def send_email(cuenta, deposito):
    # Implementar la lógica para enviar correo electrónico a `cuenta.correoelectronico`
    # Notificar sobre el depósito realizado
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
