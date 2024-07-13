import boto3

from botocore.exceptions import ClientError

db_client = boto3.resource('dynamodb', region_name='eu-west-3')

class BaseTable:

    def __init__(self, table_name):
        self.table_name = table_name
        self.dyn_resource = db_client
        if not self.exists():
            self.create_table()
    
    def exists(self):
        try:
            table = self.dyn_resource.Table(self.table_name)
            table.load()
            exists = True
        except ClientError as err:
            if err.response["Error"]["Code"] == "ResourceNotFoundException":
                exists = False
            else:
                print(f"Could not check for existence of {self.table_name}.")
                print(f"Reason: {err.response["Error"]["Code"]}: {err.response["Error"]["Message"]}")
                raise
        else:
            self.table = table
        return exists
    
    def get_schema(self):
        raise NotImplementedError

    def create_table(self):
        key_schema, attr_def = self.get_schema()
        try:
            self.table = self.dyn_resource.create_table(
                TableName=self.table_name,
                KeySchema=key_schema,
                AttributeDefinitions=attr_def,
                ProvisionedThroughput={
                    "ReadCapacityUnits": 1,
                    "WriteCapacityUnits": 1,
                },
            )
            self.table.wait_until_exists()
        except ClientError as err:
            print(f"Could not create table {self.table_name}.")
            print(f"Reason: {err.response["Error"]["Code"]}: {err.response["Error"]["Message"]}")
            raise
    
    def add_entry(self, item, key):
        try:
            response = self.table.put_item(Item=item, ReturnValues='ALL_NEW')
        except ClientError as err:
            print(f"Could not add entry {key} to table {self.table_name}.")
            print(f"Reason: {err.response["Error"]["Code"]}: {err.response["Error"]["Message"]}")
            raise
        else:
            if "Item" in response:
                return response["Item"]
        return None

    
    def get_entry(self, query, key):    
        try:
            response = self.table.get_item(Key=query)
        except ClientError as err:
            print(f"Could not get {key} from table {self.table.name}.")
            print(f"Reason: {err.response["Error"]["Code"]}: {err.response["Error"]["Message"]}")
            raise
        else:
            if "Item" in response:
                return response["Item"]
        return None
        
    def get_query(self, condition_expr, key):
        try:
            response = self.table.query(KeyConditionExpression=condition_expr)
        except ClientError as err:
            print(f"Could not query for {key}.")
            print(f"Reason: {err.response["Error"]["Code"]}: {err.response["Error"]["Message"]}")
            raise
        else:
            if "Item" in response:
                return response["Item"]
        return None
    
    def update_entry(self, query, update_expr, expr_attr_values, key):
        try:
            response = self.table.update_item(
                Key=query,
                UpdateExpression=update_expr,
                ExpressionAttributeValues=expr_attr_values,
                ReturnValues="UPDATED_NEW",
            )
        except ClientError as err:
            print(f"Could not update {key} in table {self.table_name}.")
            print(f"Reason: {err.response["Error"]["Code"]}: {err.response["Error"]["Message"]}")
            raise
        else:
            return response["Attributes"]