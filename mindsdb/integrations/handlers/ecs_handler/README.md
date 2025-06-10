# ECS Handler for MindsDB

This handler allows MindsDB to connect to ECS (Elastic Container Service) and interact with it.

## Implementation

This handler is implemented using the ECS Python SDK. The required arguments to establish a connection are:

* `access_key` - AWS access key ID
* `secret_key` - AWS secret access key
* `region` - AWS region name
* `cluster` - ECS cluster name

## Usage

In order to make use of this handler and connect to ECS in MindsDB, the following syntax can be used:

```sql
CREATE DATABASE ecs_datasource
WITH
    engine = 'ecs',
    parameters = {
        "access_key": "your_access_key",
        "secret_key": "your_secret_key",
        "region": "your_region",
        "cluster": "your_cluster"
    };
```

You can use this established connection to query your ECS resources as follows:

```sql
SELECT *
FROM ecs_datasource.tasks;
```

## Supported Operations

The ECS handler supports the following operations:

1. List clusters
2. List services
3. List tasks
4. Get task details
5. Get service details
6. Get cluster details

## Prerequisites

Before using this handler, ensure you have:

1. AWS credentials with appropriate permissions
2. Python 3.7 or higher
3. Required Python packages installed (see requirements.txt) 