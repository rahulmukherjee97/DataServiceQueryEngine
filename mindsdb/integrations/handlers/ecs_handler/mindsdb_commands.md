# MindsDB ECS Integration Commands

## 1. Create ECS Integration
```sql
CREATE DATABASE ecs_integration
WITH ENGINE = 'ecs',
PARAMETERS = {
    'base_url': 'https://alpha.uipath.com',
    'account_id': '07e28361-8ca4-4078-b585-d2365754994f',
    'tenant_id': '508b9064-94b0-4bf5-b3be-7e8a7dc2b991',
    'bearer_token': 'YOUR_BEARER_TOKEN',
    'schema_id': '678ce730-cda9-4416-6d42-08dd78f3dc1d'
};
```

Alternative syntax if the above doesn't work:
```sql
CREATE DATABASE ecs_integration
WITH ENGINE = 'ecs',
PARAMETERS = '{
    "base_url": "https://alpha.uipath.com",
    "account_id": "07e28361-8ca4-4078-b585-d2365754994f",
    "tenant_id": "508b9064-94b0-4bf5-b3be-7e8a7dc2b991",
    "bearer_token": "YOUR_BEARER_TOKEN",
    "schema_id": "678ce730-cda9-4416-6d42-08dd78f3dc1d"
}';
```

## Troubleshooting Common Errors

1. **Syntax Error**
   - Make sure to use single quotes for the entire parameters string
   - Double quotes for JSON keys and values
   - No trailing commas in the JSON

2. **Connection Error**
   - Verify the bearer token is valid and not expired
   - Check if the account_id and tenant_id are correct
   - Ensure the base_url is accessible

3. **Schema Error**
   - Verify the schema_id exists in ECS
   - Make sure you have permissions to access the schema

4. **Handler Not Found**
   - Ensure the ECS handler is properly installed
   - Check if the handler name 'ecs' is correct
   - Verify the handler is in the correct directory

## Test Connection
```sql
SELECT * FROM ecs_integration.ecs
WHERE operation = 'test_connection';
```

## 2. Create Schema in ECS
```