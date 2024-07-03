import json
import boto3
from aws_cdk import core
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_apigateway as apigw
from aws_cdk import aws_dynamodb as dynamodb


class BancoSeguroLambda(lambda_.Function):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Código fuente de la función Lambda (adaptado de tu API Flask)
        def handler(event, context):
            # Simulando la consulta a la base de datos (reemplazar con DynamoDB)
            cuenta = {
                "numerodecuenta": "1234567890",
                "titular": "Juan Perez",
                "correoelectronico": "juan.perez@email.com",
                "clavetarjeta": "1234",
            }

            # Validación de la clave anterior
            if event["claveanterior"] != cuenta["clavetarjeta"]:
                raise Exception("Clave anterior incorrecta")

            # Actualización de la clave en la base de datos (reemplazar con DynamoDB)
            cuenta["clavetarjeta"] = event["clavenueva"]

            # Envío de correo electrónico de notificación (reemplazar con SES)
            send_email(cuenta["correoelectronico"], "Cambio de clave exitoso")

            return {
                "statusCode": 200,
                "body": json.dumps({"mensaje": "Clave de la tarjeta de débito cambiada exitosamente"})
            }

        # Configuración de la función Lambda
        self.handler = handler
        self.runtime = lambda_.Runtime.PYTHON_3_8
class BancoSeguroTable(dynamodb.Table):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define el esquema de la tabla
        self.partition_key = dynamodb.Attribute(name="numerodecuenta", type=dynamodb.AttributeType.STRING)
        self.titular = dynamodb.Attribute(name="titular", type=dynamodb.AttributeType.STRING)
        self.correoelectronico = dynamodb.Attribute(name="correoelectronico", type=dynamodb.AttributeType.STRING)
        self.clavetarjeta = dynamodb.Attribute(name="clavetarjeta", type=dynamodb.AttributeType.STRING)

        # Crea la tabla con el esquema definido
        self.table_name = self.create_table(
            partition_key=self.partition_key,
            time_stamp_attribute=None
        )
class BancoSeguroApi(apigw.RestApi):
    def __init__(self, scope: core.Construct, id: str, lambda_function: lambda_.Function, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Crea un recurso para la API
        resource = self.root.add_resource("banco-seguro")

        # Crea un método POST para el endpoint de cambio de clave
        change_password_integration = apigw.LambdaIntegration(lambda_function)
        resource.add_method("POST", change_password_integration, operation_name="cambiarClave")
