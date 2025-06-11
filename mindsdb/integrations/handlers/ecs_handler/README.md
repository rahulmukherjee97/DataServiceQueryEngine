# MindsDB ECS Handler

This handler integrates MindsDB with Enterprise Content Search (ECS), allowing you to perform semantic search operations on your data.

## Setup

### Prerequisites
- MindsDB installed
- ECS account with access credentials
- Bearer token for authentication

### Connection Parameters

When connecting to ECS through MindsDB, you'll need to provide the following parameters:

```sql
CREATE DATABASE ecs_integration
WITH ENGINE = 'ecs',
PARAMETERS = {
    'base_url': Base url for uipath platfrom services,
    'token': Bearer token for uipath services,
    'organization': organization name for uipath access,
    'tenant': Tenant name for which you want access to the data ,
};
```