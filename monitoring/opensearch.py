import pulumi
import pulumi_aws as aws
from pulumi import Config

def create_opensearch_cluster(vpc, private_subnets, security_groups):
    config = Config()
    master_user = config.require("opensearchMasterUser")
    master_password = config.require_secret("opensearchMasterPassword")

    opensearch_domain = aws.opensearch.Domain(
        "opensearch-domain",
        domain_name="my-opensearch-domain",
        engine_version="OpenSearch_1.0",
        cluster_config=aws.opensearch.DomainClusterConfigArgs(
            instance_type="t3.small.search",
            instance_count=2,
            zone_awareness_enabled=True,
            zone_awareness_config=aws.opensearch.DomainClusterConfigZoneAwarenessConfigArgs(
                availability_zone_count=2,
            ),
        ),
        ebs_options=aws.opensearch.DomainEbsOptionsArgs(
            ebs_enabled=True,
            volume_size=10,
            volume_type="gp2",
        ),
        vpc_options=aws.opensearch.DomainVpcOptionsArgs(
            security_group_ids=[security_groups["opensearch"].id],
            subnet_ids=[subnet.id for subnet in private_subnets],
        ),
        encrypt_at_rest=aws.opensearch.DomainEncryptAtRestArgs(
            enabled=True,
        ),
        node_to_node_encryption=aws.opensearch.DomainNodeToNodeEncryptionArgs(
            enabled=True,
        ),
        advanced_security_options=aws.opensearch.DomainAdvancedSecurityOptionsArgs(
            enabled=True,
            internal_user_database_enabled=True,
            master_user_options=aws.opensearch.DomainAdvancedSecurityOptionsMasterUserOptionsArgs(
                master_user_name=master_user,
                master_user_password=master_password,
            ),
        ),
 

          domain_endpoint_options=aws.opensearch.DomainDomainEndpointOptionsArgs(
            enforce_https=True,
        ),
        tags={"Name": "opensearch-domain"},
    )

    return opensearch_domain
