import pulumi
import pulumi_aws as aws
import json

def create_iam_roles():
    
    ecs_task_execution_role = aws.iam.Role(
        "ecs-task-execution-role",
        assume_role_policy=json.dumps({
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "sts:AssumeRole",
                    "Principal": {"Service": "ecs-tasks.amazonaws.com"},
                    "Effect": "Allow",
                }
            ],
        }),
        tags={"Name": "ecs-task-execution-role"},
    )


    aws.iam.RolePolicyAttachment(
        "ecs-task-execution-policy-attachment",
        role=ecs_task_execution_role.name,
        policy_arn="arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy",
    )

    # IAM Role for ECS Task
    ecs_task_role = aws.iam.Role(
        "ecs-task-role",
        assume_role_policy=json.dumps({
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "sts:AssumeRole",
                    "Principal": {"Service": "ecs-tasks.amazonaws.com"},
                    "Effect": "Allow",
                }
            ],
        }),
        tags={"Name": "ecs-task-role"},
    )

   
    ecs_task_policy = aws.iam.Policy(
        "ecs-task-policy",
        description="Policy for ECS tasks to access AWS services",
        policy=json.dumps({
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": [
                        "secretsmanager:GetSecretValue",
                        "kms:Decrypt"
                    ],
                    "Effect": "Allow",
                    "Resource": "*"
                },
                {
                    "Action": [
                        "logs:CreateLogStream",
                        "logs:PutLogEvents"
                    ],
                    "Effect": "Allow",
                    "Resource": "*"
                }
            ]
        }),
    )

    
    aws.iam.RolePolicyAttachment(
        "ecs-task-policy-attachment",
        role=ecs_task_role.name,
        policy_arn=ecs_task_policy.arn,
    )

    return {
        "ecs_task_execution_role": ecs_task_execution_role,
        "ecs_task_role": ecs_task_role,
    }
