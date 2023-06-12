import json
from constructs import Construct
from aws_cdk import App, Stack
from aws_cdk import aws_dynamodb as dynamodb


class UserSubscriptionPlanCLS(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        with open('f3040-b10-r105-cc-dtn-schema-fil.json') as f:
            schema = json.load(f)
        
        with open('f3040-b10-r105-cc-dtn-variable-fil.json') as f:
            environment = json.load(f)
        
        # Parse table arguments
        table_args = {
            "partition_key": dynamodb.Attribute(
                name=schema["partitionKEY"]["name"],
                type=getattr(dynamodb.AttributeType, schema["partitionKEY"]["type"]),
            ),
        #   "billing_mode": getattr(dynamodb.BillingMode, schema["billingMode"]),
        #   "removal_policy": getattr(core.RemovalPolicy, schema["removalPolicy"]),
        }
        
        if "sortKey" in schema:
            table_args["sort_key"] = dynamodb.Attribute(
                name=schema["sortKEY"]["name"],
                type=getattr(dynamodb.AttributeType, schema["sortKEY"]["type"]),
            )

        # Create the table
        table = dynamodb.Table(self, schema["tableName"], **table_args)

        # Add global secondary indexes
        for gsi in schema.get("globalSecondaryIndexes", []):
            gsi_props = {
                "index_name": gsi["indexName"],
                "partition_key": dynamodb.Attribute(
                    name=gsi["partitionKEY"]["name"],
                    type=getattr(dynamodb.AttributeType, gsi["partitionKEY"]["type"]),
                ),
                "read_capacity": gsi.get("readCapacity"),
                "write_capacity": gsi.get("writeCapacity"),
                "projection_type": getattr(dynamodb.ProjectionType, gsi["projectionType"]),
            }
            
            if "sortKey" in gsi:
                gsi_props["sort_key"] = dynamodb.Attribute(
                    name=gsi["sortKEY"]["name"],
                    type=getattr(dynamodb.AttributeType, gsi["sortKEY"]["type"]),
                )

            table.add_global_secondary_index(**gsi_props)
        
        # Add tags
        for key, value in schema.get("tags", {}).items():
            core.Tag.add(table, key, value)

        # Add Stream
        if schema.get("stream", None):
            table.add_stream(getattr(dynamodb.StreamViewType, schema["stream"]))

        # Point-in-time recovery
        if schema.get("pointInTimeRecovery", None):
            table.enable_point_in_time_recovery()


app = App()
UserSubscriptionPlanCLS(app, "f3040-b10-r105-cc-dtn-sta-sd", env={'account': '635602896676', 'region':'eu-west-2'})
app.synth()