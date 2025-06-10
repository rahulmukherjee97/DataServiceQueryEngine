---
title: UiPath Enterprise Context Service
sidebarTitle: ECS
---

This documentation describes the integration of MindsDB with [UiPath Enterprise Context Service (ECS)](https://docs.uipath.com/enterprise-context-service/), a service that provides a centralized way to store and manage context data across your automation projects.

## Prerequisites

Before proceeding, ensure the following prerequisites are met:

1. Install MindsDB locally via [Docker](/setup/self-hosted/docker) or [Docker Desktop](/setup/self-hosted/docker-desktop).
2. Have access to a UiPath Orchestrator instance with ECS enabled.
3. Have valid credentials for UiPath Orchestrator.

## Connection

Establish a connection to ECS from MindsDB by executing the following SQL command:

```sql
CREATE DATABASE ecs_datasource
WITH
  ENGINE = 'ecs',
  PARAMETERS = {
    "url": "https://cloud.uipath.com/your-account/your-instance/ecs",
    "tenant": "Default",
    "username": "your-username",
    "password": "your-password",
    "organization_unit": "Default"  -- Optional
  };
```

Required connection parameters include the following:

* `url`: The URL of your UiPath ECS instance.
* `tenant`: The tenant name in UiPath Orchestrator.
* `username`: The username for UiPath Orchestrator authentication.
* `password`: The password for UiPath Orchestrator authentication.

Optional connection parameters include the following:

* `organization_unit`: The organization unit ID in UiPath Orchestrator.

## Usage

Retrieve data from ECS using SQL queries:

```sql
-- List all contexts
SELECT * FROM ecs_datasource.contexts;

-- Get contexts with specific filters
SELECT * FROM ecs_datasource.contexts 
WHERE type = 'String' AND isDeleted = false;

-- Get contexts created after a specific date
SELECT * FROM ecs_datasource.contexts 
WHERE createdAt > '2024-01-01';
```

## Supported Operations

The ECS handler supports the following operations:

1. **SELECT Queries**
   - List all contexts
   - Filter contexts by various fields
   - Sort and limit results

2. **Native Commands**
   - `list-contexts`: List all contexts
   - `get-context <id>`: Get a specific context by ID
   - `create-context <json_data>`: Create a new context
   - `update-context <id> <json_data>`: Update an existing context
   - `delete-context <id>`: Delete a context

## Troubleshooting Guide

<Warning>
`Authentication Error`

* **Symptoms**: Failure to connect to ECS with authentication errors.
* **Checklist**:
    1. Verify that the URL is correct and accessible.
    2. Confirm that the tenant name is correct.
    3. Ensure the username and password are valid.
    4. Check if the user has the necessary permissions in UiPath Orchestrator.
</Warning>

<Warning>
`Connection Error`

* **Symptoms**: Failure to establish connection to ECS.
* **Checklist**:
    1. Ensure the ECS instance is running and accessible.
    2. Verify network connectivity to the ECS instance.
    3. Check if any firewall rules are blocking the connection.
</Warning>

<Warning>
`Operation Error`

* **Symptoms**: Errors during ECS operations.
* **Checklist**:
    1. Verify that the context ID exists when performing operations on specific contexts.
    2. Ensure the JSON data format is correct when creating or updating contexts.
    3. Check if the user has the necessary permissions for the operation.
</Warning> 