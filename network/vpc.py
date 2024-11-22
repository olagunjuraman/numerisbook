import pulumi
import pulumi_aws as aws

def create_vpc():

    vpc = aws.ec2.Vpc(
        "vpc",
        cidr_block="10.0.0.0/16",
        enable_dns_hostnames=True,
        enable_dns_support=True,
        tags={"Name": "my-vpc"},
    )


    availability_zones = aws.get_availability_zones().names[:2]

  
    public_subnets = []
    private_subnets = []

    for i, az in enumerate(availability_zones):
        public_subnet = aws.ec2.Subnet(
            f"public-subnet-{i}",
            vpc_id=vpc.id,
            cidr_block=f"10.0.{i}.0/24",
            availability_zone=az,
            map_public_ip_on_launch=True,
            tags={"Name": f"public-subnet-{i}"},
        )
        public_subnets.append(public_subnet)

        private_subnet = aws.ec2.Subnet(
            f"private-subnet-{i}",
            vpc_id=vpc.id,
            cidr_block=f"10.0.{i + 100}.0/24",
            availability_zone=az,
            map_public_ip_on_launch=False,
            tags={"Name": f"private-subnet-{i}"},
        )
        private_subnets.append(private_subnet)


    internet_gateway = aws.ec2.InternetGateway(
        "internet-gateway",
        vpc_id=vpc.id,
        tags={"Name": "internet-gateway"},
    )


    eip = aws.ec2.Eip(
        "nat-eip",
        vpc=True,
        tags={"Name": "nat-eip"},
    )

    nat_gateway = aws.ec2.NatGateway(
        "nat-gateway",
        subnet_id=public_subnets[0].id,
        allocation_id=eip.id,
        tags={"Name": "nat-gateway"},
    )

    public_route_table = aws.ec2.RouteTable(
        "public-route-table",
        vpc_id=vpc.id,
        routes=[
            aws.ec2.RouteTableRouteArgs(
                cidr_block="0.0.0.0/0",
                gateway_id=internet_gateway.id,
            )
        ],
        tags={"Name": "public-route-table"},
    )

    private_route_table = aws.ec2.RouteTable(
        "private-route-table",
        vpc_id=vpc.id,
        routes=[
            aws.ec2.RouteTableRouteArgs(
                cidr_block="0.0.0.0/0",
                nat_gateway_id=nat_gateway.id,
            )
        ],
        tags={"Name": "private-route-table"},
    )


    for subnet in public_subnets:
        aws.ec2.RouteTableAssociation(
            f"public-route-table-assoc-{subnet._name}",
            subnet_id=subnet.id,
            route_table_id=public_route_table.id,
        )

    for subnet in private_subnets:
        aws.ec2.RouteTableAssociation(
            f"private-route-table-assoc-{subnet._name}",
            subnet_id=subnet.id,
            route_table_id=private_route_table.id,
        )


    s3_endpoint = aws.ec2.VpcEndpoint(
        "s3-endpoint",
        vpc_id=vpc.id,
        service_name=f"com.amazonaws.{aws.config.region}.s3",
        route_table_ids=[public_route_table.id, private_route_table.id],
    )

    return vpc, public_subnets, private_subnets
