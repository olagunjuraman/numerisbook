import pulumi
from pulumi import Config

config = Config()


aws_region = config.get("awsRegion") or aws.config.region


db_username = config.require("dbUsername")
db_password = config.require_secret("dbPassword")


opensearch_master_user = config.require("opensearchMasterUser")
opensearch_master_password = config.require_secret("opensearchMasterPassword")
