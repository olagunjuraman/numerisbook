import pulumi
import pulumi_aws as aws
from pulumi import Config

def create_rds_instance(vpc, private_subnets, security_groups):
    config = Config()
    db_username = config.require("dbUsername")
    db_password = config.require_secret("dbPassword")


    rds_subnet_group = aws.rds.SubnetGroup(
        "rds-subnet-group",
        subnet_ids=[subnet.id for subnet in private_subnets],
        tags={"Name": "rds-subnet-group"},
    )


    rds_parameter_group = aws.rds.ParameterGroup(
        "rds-parameter-group",
        family="postgres13",
        parameters=[
            aws.rds.ParameterGroupParameterArgs(
                name="rds.force_ssl",
                value="1",
            )
        ],
        tags={"Name": "rds-parameter-group"},
    )

   
    rds_instance = aws.rds.Instance(
        "rds-instance",
        allocated_storage=20,
        max_allocated_storage=100,
        engine="postgres",
        engine_version="16.1",
        instance_class="db.t3.micro",
        db_name="mydatabase",
        username=db_username,
        password=db_password,
        db_subnet_group_name=rds_subnet_group.id,
        parameter_group_name="postgres16-parameter-group",
        vpc_security_group_ids=[security_groups["rds"].id],
        multi_az=True,
        storage_encrypted=True,
        backup_retention_period=7,
        skip_final_snapshot=True,
        tags={"Name": "rds-instance"},
    )

    return rds_instance
