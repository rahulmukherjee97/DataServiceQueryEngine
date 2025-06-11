import json
import requests
from typing import Dict, List, Optional, Union
import pandas as pd

from mindsdb.integrations.libs.api_handler import APIHandler, APITable
from mindsdb.integrations.libs.response import (
    RESPONSE_TYPE,
    HandlerResponse as Response,
    HandlerStatusResponse as StatusResponse
)
from mindsdb.utilities import log

logger = log.getLogger(__name__)

class ECSTable(APITable):
    """ECS Table implementation"""

    def select(self, query: Dict) -> pd.DataFrame:
        """Handles select query to ECS API"""
        if 'query' not in query:
            raise ValueError("Query parameter is required for search")
        
        search_query = query['query']
        schema_id = query.get('schema_id')
        threshold = query.get('threshold', 0.45)
        number_of_results = query.get('number_of_results', 3)

        # Prepare search request
        search_request = {
            "query": {
                "query": search_query,
                "threshold": threshold,
                "numberOfResults": number_of_results
            }
        }
        
        if schema_id:
            search_request["schema"] = {"id": schema_id}

        # Make API call
        response = self.handler.call_api(
            'POST',
            f'{self.handler.ecs_url}/v1/search',
            json=search_request
        )

        # Convert response to DataFrame
        results = []
        for item in response.get('results', []):
            results.append({
                'content': item.get('content'),
                'score': item.get('score'),
                'metadata': json.dumps(item.get('metadata', {}))
            })

        return pd.DataFrame(results)

    def insert(self, data: Dict) -> None:
        """Handles insert query to ECS API"""
        if 'schema' not in data:
            raise ValueError("Schema information is required for ingestion")

        # Prepare ingestion request
        ingestion_request = {
            "name": data.get('name', 'New Dataset'),
            "version": data.get('version', '1.0'),
            "type": data.get('type', 'pdf'),
            "dataSource": data.get('dataSource'),
            "schema": data['schema']
        }

        # Make API call
        self.handler.call_api(
            'POST',
            f'{self.handler.ecs_url}/v1/datasets/ingestions',
            json=ingestion_request
        )

    def create_schema(self, data: Dict) -> None:
        """Creates a new schema in ECS"""
        if 'fields' not in data:
            raise ValueError("Fields are required for schema creation")

        # Prepare schema creation request
        schema_request = {
            "name": data.get('name', 'New Schema'),
            "version": data.get('version', '1.0'),
            "fields": data['fields']
        }

        # Make API call
        self.handler.call_api(
            'POST',
            f'{self.handler.ecs_url}/v1/schemas',
            json=schema_request
        )

class ECSHandler(APIHandler):
    """This handler handles connection and execution of the ECS API."""

    name = "ecs"

    def __init__(self, name: str, **kwargs):
        super().__init__(name)
        self.connection_args = kwargs.get('connection_args', {})
        
        # Validate required parameters
        required_params = ['base_url', 'account_id', 'tenant_id', 'bearer_token', 'schema_id']
        missing_params = [param for param in required_params if not self.connection_args.get(param)]
        if missing_params:
            raise ValueError(f"Missing required parameters: {', '.join(missing_params)}")
        
        self.base_url = self.connection_args['base_url']
        self.account_id = self.connection_args['account_id']
        self.tenant_id = self.connection_args['tenant_id']
        self.bearer_token = self.connection_args['bearer_token']
        self.schema_id = self.connection_args['schema_id']
        
        # Remove trailing slash from base_url if present
        if self.base_url.endswith('/'):
            self.base_url = self.base_url[:-1]
            
        self.connected = False
        self._connect()

        self._register_table('ecs', ECSTable(self))

    def call_api(self, method: str, url: str, **kwargs) -> requests.Response:
        """Make an API call to the ECS service."""
        headers = {
            'Authorization': f'Bearer {self.bearer_token}',
            'Content-Type': 'application/json',
            'X-UiPath-AccountId': self.account_id,
            'X-UiPath-TenantId': self.tenant_id
        }
        kwargs['headers'] = headers
        return requests.request(method, url, **kwargs)

    def _construct_ecs_url(self, endpoint: str) -> str:
        """Construct the ECS URL using the base URL, account ID, and tenant ID."""
        return f"{self.base_url}/{self.account_id}/{self.tenant_id}/ecs_/{endpoint}"

    def _construct_identity_url(self, endpoint: str) -> str:
        """Construct the identity URL using the base URL."""
        return f"{self.base_url}/_identity/{endpoint}"

    def check_connection(self) -> StatusResponse:
        """Check the connection to the ECS service."""
        try:
            # Test the connection by making a simple API call
            url = f"{self.base_url}/api/v1/schemas/{self.schema_id}"
            response = self.call_api('GET', url)
            if response.status_code == 200:
                return StatusResponse(success=True)
            else:
                return StatusResponse(success=False, error_message=f"Failed to connect to ECS: {response.text}")
        except Exception as e:
            return StatusResponse(success=False, error_message=str(e))

    def _connect(self) -> None:
        """Connect to the ECS service."""
        try:
            # Test the connection
            status = self.check_connection()
            if not status.success:
                raise Exception(status.error_message)
            self.connected = True
        except Exception as e:
            self.connected = False
            raise Exception(f"Failed to connect to ECS: {str(e)}")