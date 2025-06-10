import requests
from typing import Dict, List, Optional, Any, Union
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class ECSWrapperError(Exception):
    """Base exception class for ECS wrapper errors."""
    pass

class ECSConnectionError(ECSWrapperError):
    """Exception raised for connection-related errors."""
    pass

class ECSOperationError(ECSWrapperError):
    """Exception raised for operation-related errors."""
    pass

class ECSWrapper:
    """
    A wrapper class for UiPath Enterprise Context Service operations.
    This class provides a simplified interface to interact with UiPath ECS.
    """
    
    def __init__(self, url: str, tenant: str, username: str, password: str, organization_unit: Optional[str] = None):
        """
        Initialize the ECS wrapper.
        
        Args:
            url (str): The URL of the UiPath ECS instance
            tenant (str): The tenant name in UiPath Orchestrator
            username (str): The username for authentication
            password (str): The password for authentication
            organization_unit (Optional[str]): The organization unit ID
        """
        self.base_url = url.rstrip('/')
        self.tenant = tenant
        self.username = username
        self.password = password
        self.organization_unit = organization_unit
        self.session = requests.Session()
        self.token = None
        
        # Initialize connection
        self._authenticate()

    def _authenticate(self) -> None:
        """
        Authenticate with UiPath Orchestrator and get access token.
        """
        try:
            auth_url = f"{self.base_url}/api/account/authenticate"
            auth_data = {
                "tenancyName": self.tenant,
                "usernameOrEmailAddress": self.username,
                "password": self.password
            }
            
            response = self.session.post(auth_url, json=auth_data)
            response.raise_for_status()
            
            auth_result = response.json()
            self.token = auth_result.get('result', {}).get('accessToken')
            
            if not self.token:
                raise ECSConnectionError("Failed to obtain access token")
                
            # Set authorization header for future requests
            self.session.headers.update({
                'Authorization': f'Bearer {self.token}'
            })
            
        except requests.exceptions.RequestException as e:
            raise ECSConnectionError(f"Authentication failed: {str(e)}")

    def check_connection(self) -> bool:
        """
        Check if the connection to ECS is working.
        
        Returns:
            bool: True if connection is successful, False otherwise
        """
        try:
            response = self.session.get(f"{self.base_url}/api/services/app/Context/GetContexts")
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Error checking ECS connection: {e}")
            return False

    def get_contexts(self, max_results: int = 100) -> List[Dict[str, Any]]:
        """
        Get all contexts from ECS.
        
        Args:
            max_results (int): Maximum number of results to return
            
        Returns:
            List[Dict[str, Any]]: List of context information
        """
        try:
            response = self.session.get(
                f"{self.base_url}/api/services/app/Context/GetContexts",
                params={'maxResultCount': max_results}
            )
            response.raise_for_status()
            return response.json().get('result', {}).get('items', [])
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting contexts: {e}")
            raise ECSOperationError(f"Failed to get contexts: {str(e)}")

    def get_context_by_id(self, context_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific context by ID.
        
        Args:
            context_id (str): The ID of the context to retrieve
            
        Returns:
            Optional[Dict[str, Any]]: Context details or None if not found
        """
        try:
            response = self.session.get(
                f"{self.base_url}/api/services/app/Context/GetContext",
                params={'id': context_id}
            )
            response.raise_for_status()
            return response.json().get('result')
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting context: {e}")
            raise ECSOperationError(f"Failed to get context: {str(e)}")

    def create_context(self, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new context.
        
        Args:
            context_data (Dict[str, Any]): The context data to create
            
        Returns:
            Dict[str, Any]: The created context
        """
        try:
            response = self.session.post(
                f"{self.base_url}/api/services/app/Context/CreateContext",
                json=context_data
            )
            response.raise_for_status()
            return response.json().get('result')
        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating context: {e}")
            raise ECSOperationError(f"Failed to create context: {str(e)}")

    def update_context(self, context_id: str, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing context.
        
        Args:
            context_id (str): The ID of the context to update
            context_data (Dict[str, Any]): The updated context data
            
        Returns:
            Dict[str, Any]: The updated context
        """
        try:
            context_data['id'] = context_id
            response = self.session.put(
                f"{self.base_url}/api/services/app/Context/UpdateContext",
                json=context_data
            )
            response.raise_for_status()
            return response.json().get('result')
        except requests.exceptions.RequestException as e:
            logger.error(f"Error updating context: {e}")
            raise ECSOperationError(f"Failed to update context: {str(e)}")

    def delete_context(self, context_id: str) -> bool:
        """
        Delete a context.
        
        Args:
            context_id (str): The ID of the context to delete
            
        Returns:
            bool: True if deletion was successful
        """
        try:
            response = self.session.delete(
                f"{self.base_url}/api/services/app/Context/DeleteContext",
                params={'id': context_id}
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Error deleting context: {e}")
            raise ECSOperationError(f"Failed to delete context: {str(e)}")

    def execute_command(self, command: str) -> Dict[str, Any]:
        """
        Execute a raw command.
        This is a simplified version that supports basic ECS operations.
        
        Args:
            command (str): The command to execute
            
        Returns:
            Dict[str, Any]: Command execution result
        """
        try:
            # Parse the command and execute appropriate method
            parts = command.split()
            if not parts:
                raise ValueError("Empty command")

            cmd = parts[0]
            args = parts[1:]

            if cmd == 'list-contexts':
                max_results = self._parse_max_results(args)
                return {'contexts': self.get_contexts(max_results)}
            elif cmd == 'get-context':
                if not args:
                    raise ValueError("Context ID required")
                return {'context': self.get_context_by_id(args[0])}
            elif cmd == 'create-context':
                if not args:
                    raise ValueError("Context data required")
                context_data = json.loads(' '.join(args))
                return {'context': self.create_context(context_data)}
            elif cmd == 'update-context':
                if len(args) < 2:
                    raise ValueError("Context ID and data required")
                context_id = args[0]
                context_data = json.loads(' '.join(args[1:]))
                return {'context': self.update_context(context_id, context_data)}
            elif cmd == 'delete-context':
                if not args:
                    raise ValueError("Context ID required")
                return {'success': self.delete_context(args[0])}
            else:
                raise ValueError(f"Unsupported command: {cmd}")
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            return {'error': str(e)}

    def _parse_max_results(self, args: List[str]) -> int:
        """Parse max results from command arguments."""
        try:
            for i, arg in enumerate(args):
                if arg == '--max-results' and i + 1 < len(args):
                    return int(args[i + 1])
        except (ValueError, IndexError):
            pass
        return 100  # Default value 