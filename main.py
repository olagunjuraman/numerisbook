import sys
import os


current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

import pulumi


from network.vpc import create_vpc
from security.security_groups import create_security_groups
from security.iam_roles import create_iam_roles
from compute.ecs_cluster import create_ecs_cluster
from data.rds_instance import create_rds_instance
from monitoring.opensearch import create_opensearch_cluster


vpc, public_subnets, private_subnets = create_vpc()


security_groups = create_security_groups(vpc)


iam_roles = create_iam_roles()


ecs_cluster = create_ecs_cluster(
    vpc=vpc,
    private_subnets=private_subnets,
    public_subnets=public_subnets,
    security_groups=security_groups,
    iam_roles=iam_roles,
)


rds_instance = create_rds_instance(
    vpc=vpc,
    private_subnets=private_subnets,
    security_groups=security_groups,
)


opensearch_cluster = create_opensearch_cluster(
    vpc=vpc,
    private_subnets=private_subnets,
    security_groups=security_groups,
)


pulumi.export("vpc_id", vpc.id)
pulumi.export("ecs_cluster_name", ecs_cluster.name)
pulumi.export("rds_endpoint", rds_instance.endpoint)
pulumi.export("opensearch_endpoint", opensearch_cluster.endpoint)
