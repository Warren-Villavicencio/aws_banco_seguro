from aws_cdk import core
from aws_cdk.aws_lambda import Function, Code, Runtime
from aws_cdk.aws_ses import EmailIdentity, EmailTemplate, ReceiptRule, SnsTopic
from botocore.exceptions import ClientError

class PasswordChangeLambdaStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Define environment variables (replace placeholders with actual values)
        self.sender_email_address = core.StringParameter(self, "SenderEmailAddress", string_value="your_email@example.com")
        self.recipient_email_address = core.StringParameter(self, "RecipientEmailAddress", string_value="placeholder@example.com")

        # Create a Lambda function to handle password changes
        self.password_change_function = Function(
            self,
            "PasswordChangeFunction",
            runtime=Runtime.PYTHON_3_9,
            code=Code.asset("lambda_code"),  # Replace with path to your Lambda code
            handler="lambda_handler.handler"  # Replace with your handler function name
        )

        # Verify recipient email address with SES (optional, for improved deliverability)
        try:
            ses_client = boto3.client("ses")
            ses_client.verify_email_identity(EmailAddress=self.recipient_email_address.value)
        except ClientError as e:
            if e.response['Error']['Code'] == 'VerificationInProgress':
                print("Recipient email verification already in progress.")
            else:
                raise e

        # Create an SES email template for password change notifications (optional)
        self.password_change_template = EmailTemplate(
            self,
            "PasswordChangeTemplate",
            template_name="PasswordChangeNotification",
            subject="Notification of Password Change - Banco Seguro",
            text_part=EmailTemplate.TextPart(
                charset="UTF-8",
                data="""
                BANCO-SEGURO

                Le informamos {cuenta.titular}, el siguiente reporte de transacción.

                La clave de la tarjeta de débito asociada a la cuenta |- {datos_cambio.numerodecuenta} -| ha sido cambiada exitosamente.

                Fecha y hora de la transacción: |- {transaction_time} -|
                """
            )
        )

        # Create an SNS topic for sending email notifications
        self.email_notification_topic = SnsTopic(self, "EmailNotificationTopic")

        # Configure a receipt rule (optional) to trigger the Lambda function upon account updates
        # (requires additional configuration in your application)
        # receipt_rule = ReceiptRule(
        #     self,
        #     "AccountUpdateRule",
        #     recipients=[self.recipient_email_address.value],
        #     rule_set_name="your_rule_set_name",
        #     actions=[
        #         SnsAction(topic=self.email_notification_topic)
        #     ]
        # )

        # Grant the Lambda function permissions to publish to the SNS topic and access SES
        self.password_change_function.add_to_role(
            self.password_change_function.role.add_service_principal("ses.amazonaws.com"))
        self.password_change_function.add_to_role(
            self.password_change_function.role.
