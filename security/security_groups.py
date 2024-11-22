import pulumi
import pulumi_aws as aws

def create_security_groups(vpc):
    
    ecs_security_group = aws.ec2.SecurityGroup(
        "ecs-security-group",
        vpc_id=vpc.id,
        description="Allow HTTP traffic to ECS tasks",
        ingress=[
            aws.ec2.SecurityGroupIngressArgs(
                protocol="tcp",
                from_port=80,
                to_port=80,
                cidr_blocks=["0.0.0.0/0"],
                description="Allow HTTP traffic from anywhere",
            ),
            aws.ec2.SecurityGroupIngressArgs(
                protocol="tcp",
                from_port=443,
                to_port=443,
                cidr_blocks=["0.0.0.0/0"],
                description="Allow HTTPS traffic from anywhere",
            ),
        ],
        egress=[
            aws.ec2.SecurityGroupEgressArgs(
                protocol="-1",
                from_port=0,
                to_port=0,
                cidr_blocks=["0.0.0.0/0"],
                description="Allow all outbound traffic",
            ),
        ],
        tags={"Name": "ecs-security-group"},
    )


    rds_security_group = aws.ec2.SecurityGroup(
        "rds-security-group",
        vpc_id=vpc.id,
        description="Allow traffic to RDS",
        ingress=[
            aws.ec2.SecurityGroupIngressArgs(
                protocol="tcp",
                from_port=5432,
                to_port=5432,
                security_groups=[ecs_security_group.id],
                description="Allow PostgreSQL from ECS tasks",
            ),
        ],
        egress=[
            aws.ec2.SecurityGroupEgressArgs(
                protocol="-1",
                from_port=0,
                to_port=0,
                cidr_blocks=["0.0.0.0/0"],
                description="Allow all outbound traffic",
            ),
        ],
        tags={"Name": "rds-security-group"},
    )


    opensearch_security_group = aws.ec2.SecurityGroup(
        "opensearch-security-group",
        vpc_id=vpc.id,
        description="Allow traffic to OpenSearch",
        ingress=[
            aws.ec2.SecurityGroupIngressArgs(
                protocol="tcp",
                from_port=443,
                to_port=443,
                security_groups=[ecs_security_group.id],
                description="Allow HTTPS from ECS tasks",
            ),
        ],
        egress=[
            aws.ec2.SecurityGroupEgressArgs(
                protocol="-1",
                from_port=0,
                to_port=0,
                cidr_blocks=["0.0.0.0/0"],
                description="Allow all outbound traffic",
            ),
        ],
        tags={"Name": "opensearch-security-group"},
    )

    return {
        "ecs": ecs_security_group,
        "rds": rds_security_group,
        "opensearch": opensearch_security_group,
    }
