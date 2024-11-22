import pulumi
import pulumi_aws as aws
import json

def create_ecs_cluster(vpc, private_subnets, public_subnets, security_groups, iam_roles):

    ecs_cluster = aws.ecs.Cluster(
        "ecs-cluster",
        name="my-ecs-cluster",
        tags={"Name": "ecs-cluster"},
    )


    alb = aws.lb.LoadBalancer(
        "alb",
        internal=False,
        security_groups=[security_groups["ecs"].id],
        subnets=[subnet.id for subnet in public_subnets],
        tags={"Name": "alb"},
    )

   
    target_group = aws.lb.TargetGroup(
        "ecs-target-group",
        port=80,
        protocol="HTTP",
        target_type="ip",
        vpc_id=vpc.id,
        health_check=aws.lb.TargetGroupHealthCheckArgs(
            path="/",
            protocol="HTTP",
            interval=30,
            timeout=5,
            healthy_threshold=5,
            unhealthy_threshold=2,
        ),
        tags={"Name": "ecs-target-group"},
    )


    listener = aws.lb.Listener(
        "alb-listener",
        load_balancer_arn=alb.arn,
        port=80,
        protocol="HTTP",
        default_actions=[
            aws.lb.ListenerDefaultActionArgs(
                type="forward",
                target_group_arn=target_group.arn,
            )
        ],
    )


    task_definition = aws.ecs.TaskDefinition(
        "ecs-task-definition",
        family="my-ecs-task",
        cpu="256",
        memory="512",
        network_mode="awsvpc",
        requires_compatibilities=["FARGATE"],
        execution_role_arn=iam_roles["ecs_task_execution_role"].arn,
        task_role_arn=iam_roles["ecs_task_role"].arn,
        container_definitions=json.dumps([{
            "name": "my-container",
            "image": "nginx",  
            "portMappings": [{
                "containerPort": 80,
                "protocol": "tcp",
            }],
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                    "awslogs-group": "/ecs/my-ecs-task",
                    "awslogs-region": aws.config.region,
                    "awslogs-stream-prefix": "ecs",
                },
            },
        }]),
        tags={"Name": "ecs-task-definition"},
    )


    ecs_service = aws.ecs.Service(
        "ecs-service",
        cluster=ecs_cluster.arn,
        desired_count=2,
        launch_type="FARGATE",
        task_definition=task_definition.arn,
        network_configuration=aws.ecs.ServiceNetworkConfigurationArgs(
            assign_public_ip=False,
            subnets=[subnet.id for subnet in private_subnets],
            security_groups=[security_groups["ecs"].id],
        ),
        load_balancers=[
            aws.ecs.ServiceLoadBalancerArgs(
                target_group_arn=target_group.arn,
                container_name="my-container",
                container_port=80,
            )
        ],
        opts=pulumi.ResourceOptions(depends_on=[listener]),
        tags={"Name": "ecs-service"},
    )

    return ecs_cluster
