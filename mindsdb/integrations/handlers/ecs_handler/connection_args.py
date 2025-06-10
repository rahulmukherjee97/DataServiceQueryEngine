from collections import OrderedDict

from mindsdb.integrations.libs.const import HANDLER_CONNECTION_ARG_TYPE as ARG_TYPE


connection_args = OrderedDict(
    url={
        'type': ARG_TYPE.STR,
        'description': 'The URL of the UiPath Enterprise Context Service.',
        'required': True,
        'label': 'ECS URL'
    },
    tenant={
        'type': ARG_TYPE.STR,
        'description': 'The tenant name in UiPath Orchestrator.',
        'required': True,
        'label': 'Tenant'
    },
    username={
        'type': ARG_TYPE.STR,
        'description': 'The username for UiPath Orchestrator authentication.',
        'required': True,
        'label': 'Username'
    },
    password={
        'type': ARG_TYPE.PWD,
        'description': 'The password for UiPath Orchestrator authentication.',
        'required': True,
        'label': 'Password',
        'secret': True
    },
    organization_unit={
        'type': ARG_TYPE.STR,
        'description': 'The organization unit ID in UiPath Orchestrator.',
        'required': False,
        'label': 'Organization Unit'
    }
)

connection_args_example = OrderedDict(
    url='https://cloud.uipath.com/your-account/your-instance/ecs',
    tenant='Default',
    username='admin',
    password='password',
    organization_unit='Default'
) 