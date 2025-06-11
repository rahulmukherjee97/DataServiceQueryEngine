from collections import OrderedDict

from mindsdb.integrations.libs.const import HANDLER_CONNECTION_ARG_TYPE as ARG_TYPE

connection_args = OrderedDict(
    ecs_url={
        "type": ARG_TYPE.STR,
        "description": "The URL of the ECS service",
        "required": True,
        "label": "ECS URL",
    },
    identity_url={
        "type": ARG_TYPE.STR,
        "description": "The URL of the identity service for authentication",
        "required": True,
        "label": "Identity URL",
    },
    bearer={
        "type": ARG_TYPE.STR,
        "description": "The Bearer for authentication",
        "required": True,
        "label": "Bearer Token",
    },
    account_id={
        "type": ARG_TYPE.STR,
        "description": "The account ID for the ECS service",
        "required": True,
        "label": "Account ID",
    },
    tenant_id={
        "type": ARG_TYPE.STR,
        "description": "The tenant ID for the ECS service",
        "required": True,
        "label": "Tenant ID",
    }
)

connection_args_example = OrderedDict(
    ecs_url="https://ecs.example.com",
    identity_url="https://identity.example.com",
    client_id="your-client-id",
    client_secret="your-client-secret",
    account_id="your-account-id",
    tenant_id="your-tenant-id"
) 