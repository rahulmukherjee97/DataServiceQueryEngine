import boto3
from typing import Dict, List, Optional, Any, Union
from botocore.exceptions import ClientError, ParamValidationError
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
    A wrapper class for AWS ECS operations.
    This class provides a simplified interface to interact with AWS ECS.
    """
    
    def __init__(self, access_key: str, secret_key: str, region: str, cluster: str):
        """
        Initialize the ECS wrapper.
        
        Args:
            access_key (str): AWS access key ID
            secret_key (str): AWS secret access key
            region (str): AWS region name
            cluster (str): ECS cluster name
        """
        self.cluster = cluster
        try:
            self.client = boto3.client(
                'ecs',
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region
            )
        except Exception as e:
            raise ECSConnectionError(f"Failed to initialize ECS client: {str(e)}")

    def check_connection(self) -> bool:
        """
        Check if the connection to ECS is working.
        
        Returns:
            bool: True if connection is successful, False otherwise
        """
        try:
            self.client.describe_clusters(clusters=[self.cluster])
            return True
        except ClientError as e:
            logger.error(f"Error checking ECS connection: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error checking ECS connection: {e}")
            return False

    def list_clusters(self, max_results: int = 100) -> List[Dict[str, Any]]:
        """
        List all ECS clusters.
        
        Args:
            max_results (int): Maximum number of results to return
            
        Returns:
            List[Dict[str, Any]]: List of cluster information
        """
        try:
            response = self.client.list_clusters(maxResults=max_results)
            if not response['clusterArns']:
                return []
            
            clusters = self.client.describe_clusters(clusters=response['clusterArns'])
            return self._format_cluster_data(clusters['clusters'])
        except ClientError as e:
            logger.error(f"Error listing clusters: {e}")
            raise ECSOperationError(f"Failed to list clusters: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error listing clusters: {e}")
            raise ECSOperationError(f"Unexpected error listing clusters: {str(e)}")

    def list_services(self, max_results: int = 100) -> List[Dict[str, Any]]:
        """
        List all services in the specified cluster.
        
        Args:
            max_results (int): Maximum number of results to return
            
        Returns:
            List[Dict[str, Any]]: List of service information
        """
        try:
            response = self.client.list_services(
                cluster=self.cluster,
                maxResults=max_results
            )
            if not response['serviceArns']:
                return []
            
            services = self.client.describe_services(
                cluster=self.cluster,
                services=response['serviceArns']
            )
            return self._format_service_data(services['services'])
        except ClientError as e:
            logger.error(f"Error listing services: {e}")
            raise ECSOperationError(f"Failed to list services: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error listing services: {e}")
            raise ECSOperationError(f"Unexpected error listing services: {str(e)}")

    def list_tasks(self, max_results: int = 100) -> List[Dict[str, Any]]:
        """
        List all tasks in the specified cluster.
        
        Args:
            max_results (int): Maximum number of results to return
            
        Returns:
            List[Dict[str, Any]]: List of task information
        """
        try:
            response = self.client.list_tasks(
                cluster=self.cluster,
                maxResults=max_results
            )
            if not response['taskArns']:
                return []
            
            tasks = self.client.describe_tasks(
                cluster=self.cluster,
                tasks=response['taskArns']
            )
            return self._format_task_data(tasks['tasks'])
        except ClientError as e:
            logger.error(f"Error listing tasks: {e}")
            raise ECSOperationError(f"Failed to list tasks: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error listing tasks: {e}")
            raise ECSOperationError(f"Unexpected error listing tasks: {str(e)}")

    def get_cluster_details(self) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about the specified cluster.
        
        Returns:
            Optional[Dict[str, Any]]: Cluster details or None if not found
        """
        try:
            response = self.client.describe_clusters(clusters=[self.cluster])
            if response['clusters']:
                return self._format_cluster_data([response['clusters'][0]])[0]
            return None
        except ClientError as e:
            logger.error(f"Error getting cluster details: {e}")
            raise ECSOperationError(f"Failed to get cluster details: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error getting cluster details: {e}")
            raise ECSOperationError(f"Unexpected error getting cluster details: {str(e)}")

    def get_service_details(self, service_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific service.
        
        Args:
            service_name (str): Name of the service
            
        Returns:
            Optional[Dict[str, Any]]: Service details or None if not found
        """
        try:
            response = self.client.describe_services(
                cluster=self.cluster,
                services=[service_name]
            )
            if response['services']:
                return self._format_service_data([response['services'][0]])[0]
            return None
        except ClientError as e:
            logger.error(f"Error getting service details: {e}")
            raise ECSOperationError(f"Failed to get service details: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error getting service details: {e}")
            raise ECSOperationError(f"Unexpected error getting service details: {str(e)}")

    def get_task_details(self, task_arn: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific task.
        
        Args:
            task_arn (str): ARN of the task
            
        Returns:
            Optional[Dict[str, Any]]: Task details or None if not found
        """
        try:
            response = self.client.describe_tasks(
                cluster=self.cluster,
                tasks=[task_arn]
            )
            if response['tasks']:
                return self._format_task_data([response['tasks'][0]])[0]
            return None
        except ClientError as e:
            logger.error(f"Error getting task details: {e}")
            raise ECSOperationError(f"Failed to get task details: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error getting task details: {e}")
            raise ECSOperationError(f"Unexpected error getting task details: {str(e)}")

    def execute_command(self, command: str) -> Dict[str, Any]:
        """
        Execute a raw AWS CLI-style command.
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

            if cmd == 'list-clusters':
                max_results = self._parse_max_results(args)
                return {'clusters': self.list_clusters(max_results)}
            elif cmd == 'list-services':
                max_results = self._parse_max_results(args)
                return {'services': self.list_services(max_results)}
            elif cmd == 'list-tasks':
                max_results = self._parse_max_results(args)
                return {'tasks': self.list_tasks(max_results)}
            elif cmd == 'get-cluster':
                return {'cluster': self.get_cluster_details()}
            elif cmd == 'get-service':
                if not args:
                    raise ValueError("Service name required")
                return {'service': self.get_service_details(args[0])}
            elif cmd == 'get-task':
                if not args:
                    raise ValueError("Task ARN required")
                return {'task': self.get_task_details(args[0])}
            else:
                raise ValueError(f"Unsupported command: {cmd}")
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            return {'error': str(e)}

    def _format_cluster_data(self, clusters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format cluster data for consistent output."""
        formatted = []
        for cluster in clusters:
            formatted.append({
                'clusterArn': cluster.get('clusterArn'),
                'clusterName': cluster.get('clusterName'),
                'status': cluster.get('status'),
                'activeServicesCount': cluster.get('activeServicesCount'),
                'runningTasksCount': cluster.get('runningTasksCount'),
                'pendingTasksCount': cluster.get('pendingTasksCount'),
                'registeredContainerInstancesCount': cluster.get('registeredContainerInstancesCount'),
                'capacityProviders': cluster.get('capacityProviders', []),
                'defaultCapacityProviderStrategy': cluster.get('defaultCapacityProviderStrategy', []),
                'tags': cluster.get('tags', [])
            })
        return formatted

    def _format_service_data(self, services: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format service data for consistent output."""
        formatted = []
        for service in services:
            formatted.append({
                'serviceArn': service.get('serviceArn'),
                'serviceName': service.get('serviceName'),
                'status': service.get('status'),
                'desiredCount': service.get('desiredCount'),
                'runningCount': service.get('runningCount'),
                'pendingCount': service.get('pendingCount'),
                'launchType': service.get('launchType'),
                'taskDefinition': service.get('taskDefinition'),
                'deploymentConfiguration': service.get('deploymentConfiguration'),
                'events': service.get('events', []),
                'tags': service.get('tags', [])
            })
        return formatted

    def _format_task_data(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format task data for consistent output."""
        formatted = []
        for task in tasks:
            formatted.append({
                'taskArn': task.get('taskArn'),
                'taskDefinition': task.get('taskDefinition'),
                'status': task.get('status'),
                'startedAt': task.get('startedAt'),
                'stoppedAt': task.get('stoppedAt'),
                'launchType': task.get('launchType'),
                'containers': task.get('containers', []),
                'lastStatus': task.get('lastStatus'),
                'desiredStatus': task.get('desiredStatus'),
                'cpu': task.get('cpu'),
                'memory': task.get('memory'),
                'tags': task.get('tags', [])
            })
        return formatted

    def _parse_max_results(self, args: List[str]) -> int:
        """Parse max results from command arguments."""
        try:
            for i, arg in enumerate(args):
                if arg == '--max-results' and i + 1 < len(args):
                    return int(args[i + 1])
        except (ValueError, IndexError):
            pass
        return 100  # Default value 