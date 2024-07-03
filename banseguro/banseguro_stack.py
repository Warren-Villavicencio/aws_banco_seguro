from constructs import Construct
from aws_cdk import (
    Duration,
    Stack,
    aws_iam as iam,
    aws_sqs as sqs,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
)
from aws_cdk import (
    aws_rds as rds,
    aws_secretsmanager as secretsmanager,
    Stack,
    Construct,
)

from aws_cdk import (
    aws_apigateway as apigw,
    Stack,
    Construct,
)

class BanseguroStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)


        db_credentials_secret = secretsmanager.Secret(self, "DBCredentialsSecret")
        database = rds.DatabaseInstance(
            self,
            "Database",
            engine=rds.DatabaseInstanceEngine.mysql(
                version=rds.MysqlEngineVersion.VER_8_0_19
            ),
            credentials=rds.Credentials.from_secret(db_credentials_secret),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.MICRO
            ),
            allocated_storage=20,
            database_name="banco_seguro",
        )


   # Define the gAPI Gateway
        api = apigw.RestApi(self, "banco_seguro_api")

        # Define the API Gateway resources and methods
        cuentas = api.root.add_resource

        queue = sqs.Queue(
            self, "BanseguroQueue",
            visibility_timeout=Duration.seconds(300),
        )

        topic = sns.Topic(
            self, "BanseguroTopic"
        )

        topic.add_subscription(subs.SqsSubscription(queue))
