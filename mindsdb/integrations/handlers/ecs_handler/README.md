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
    'base_url': 'https://alpha.uipath.com',
    'account_id': 'your-account-id',
    'tenant_id': 'your-tenant-id',
    'bearer_token': 'your-bearer-token',
    'schema_id': 'your-schema-id'
};
```

#### Parameters Explained:
- `base_url`: The base URL of your ECS service (e.g., 'https://alpha.uipath.com')
- `account_id`: Your ECS account ID
- `tenant_id`: Your ECS tenant ID
- `bearer_token`: Authentication token for ECS
- `schema_id`: The schema ID to use for operations (created via ECS API)

## Usage

### Creating a Schema

Before using the ECS handler, you need to create a schema in ECS. You can do this using the ECS API:

```bash
curl --location 'https://alpha.uipath.com/{account_id}/{tenant_id}/ecs_/v2/indexes/create' \
--header 'Authorization: Bearer {bearer_token}' \
--header 'Content-Type: application/json' \
--data-raw '{
    "name": "your_schema_name",
    "fields": [
        {
            "name": "content",
            "type": "text"
        },
        {
            "name": "metadata",
            "type": "json"
        }
    ]
}'
```

### Querying Data

Once connected, you can query your ECS data using SQL:

```sql
SELECT * FROM ecs_integration.ecs
WHERE query = 'your search query'
AND schema_id = 'your_schema_id'
AND threshold = 0.7
AND number_of_results = 10;
```

### Ingesting Data

To ingest data into your ECS index:

```sql
INSERT INTO ecs_integration.ecs (schema, data)
VALUES (
    'your_schema_id',
    '{
        "content": "your content",
        "metadata": {"key": "value"}
    }'
);
```

## Features

- Semantic search capabilities
- Support for metadata filtering
- Configurable search thresholds
- Customizable number of results
- JSON metadata support

## Error Handling

The handler includes comprehensive error handling for:
- Authentication failures
- Invalid schema IDs
- API connection issues
- Invalid query parameters

## Examples

### Basic Search
```sql
SELECT * FROM ecs_integration.ecs
WHERE query = 'search term';
```

### Search with Metadata Filter
```sql
SELECT * FROM ecs_integration.ecs
WHERE query = 'search term'
AND metadata = '{"category": "documentation"}';
```

### Search with Custom Parameters
```sql
SELECT * FROM ecs_integration.ecs
WHERE query = 'search term'
AND threshold = 0.8
AND number_of_results = 5;
```

## Troubleshooting

Common issues and solutions:

1. **Authentication Error**
   - Verify your bearer token is valid
   - Check if the token has expired

2. **Schema Not Found**
   - Ensure the schema_id exists in ECS
   - Verify you have permissions to access the schema

3. **Connection Issues**
   - Check your base_url is correct
   - Verify network connectivity
   - Ensure account_id and tenant_id are correct

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 