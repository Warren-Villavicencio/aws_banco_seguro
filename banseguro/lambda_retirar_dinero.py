class BancoSeguroRetiroLambda(lambda_.Function):
    def __init__(self, scope: core.Construct, id: str, table: dynamodb.Table, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        
        def handler(event, context):
           
            cuenta = table.get_item(key={"numerodecuenta": event["numerodecuenta"]})["Item"]

            if not cuenta:
                raise Exception("Cuenta no encontrada")

            if float(cuenta["saldo"]) < float(event["monto"]):
                raise Exception("Saldo insuficiente")

            
            cuenta["saldo"] = str(float(cuenta["saldo"]) - float(event["monto"]))
            table.put_item(Item=cuenta)

           
            send_email(cuenta["correoelectronico"], "Retiro de dinero exitoso", event["monto"], cuenta["saldo"])

            return {
                "statusCode": 200,
                "body": json.dumps({"mensaje": "Retiro realizado exitosamente", "saldo_actual": cuenta["saldo"]})
            }

        
        self.handler = handler
        self.runtime = lambda_.Runtime.PYTHON_3_8

class BancoSeguroApi(apigw.RestApi):
   

    def __init__(self, scope: core.Construct, id: str, lambda_function: lambda_.Function, table: dynamodb.Table, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

     
        resource = self.root.add_resource("banco-seguro")

     
        change_password_integration = apigw.LambdaIntegration(lambda_function)
        resource.add_method("POST", change_password_integration, operation_name="cambiarClave")

       
        withdraw_money_integration = apigw.LambdaIntegration(lambda_function)
        resource.add_method("POST", withdraw_money_integration, operation_name="retirarDinero")
