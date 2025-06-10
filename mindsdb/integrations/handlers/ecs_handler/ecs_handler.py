from typing import Optional, Any, List, Dict
from mindsdb_sql.parser.ast.base import ASTNode
from mindsdb_sql.parser.ast import Select, Identifier, BinaryOperation, Constant
import pandas as pd

from mindsdb.integrations.libs.base import DatabaseHandler
from mindsdb.integrations.libs.response import (
    HandlerStatusResponse as StatusResponse,
    HandlerResponse as Response,
    RESPONSE_TYPE
)
from mindsdb.utilities import log
from .ecs_wrapper import ECSWrapper

logger = log.getLogger(__name__)

class ECSHandler(DatabaseHandler):
    """
    This handler handles connection and execution of the ECS statements.
    """
    name = 'ecs'

    def __init__(self, name: str, connection_data: Optional[dict], **kwargs):
        """
        Initialize the handler.
        Args:
            name (str): name of particular handler instance
            connection_data (dict): parameters for connecting to the database
            **kwargs: arbitrary keyword arguments.
        """
        super().__init__(name)
        self.connection_data = connection_data
        self.is_connected = False
        self.connection = None
        self.cluster = connection_data.get('cluster')
        
        # Validate required connection parameters
        required_params = ['access_key', 'secret_key', 'region', 'cluster']
        missing_params = [param for param in required_params if param not in connection_data]
        if missing_params:
            raise ValueError(f"Missing required connection parameters: {', '.join(missing_params)}")

    def connect(self) -> StatusResponse:
        """
        Set up the connection required by the handler.
        Returns:
            HandlerStatusResponse
        """
        if self.is_connected is True:
            return self.connection

        try:
            self.connection = ECSWrapper(
                access_key=self.connection_data['access_key'],
                secret_key=self.connection_data['secret_key'],
                region=self.connection_data['region'],
                cluster=self.connection_data['cluster']
            )
            self.is_connected = True
            return StatusResponse(True)
        except Exception as e:
            logger.error(f'Error connecting to ECS: {e}!')
            return StatusResponse(False, error_message=str(e))

    def disconnect(self):
        """
        Close any existing connections.
        """
        if self.is_connected is False:
            return
        try:
            self.connection = None
            self.is_connected = False
        except Exception as e:
            logger.error(f'Error disconnecting from ECS: {e}!')

    def check_connection(self) -> StatusResponse:
        """
        Check connection to the handler.
        Returns:
            HandlerStatusResponse
        """
        response = StatusResponse(False)
        need_to_close = self.is_connected is False

        try:
            self.connect()
            if self.connection.check_connection():
                response.success = True
            else:
                response.error_message = "Failed to connect to ECS"
        except Exception as e:
            logger.error(f'Error connecting to ECS: {e}!')
            response.error_message = str(e)
        finally:
            if response.success is True and need_to_close:
                self.disconnect()
            if response.success is False and self.is_connected is True:
                self.is_connected = False

        return response

    def _handle_select(self, query: Select) -> Response:
        """
        Handle SELECT queries.
        Args:
            query (Select): The SELECT query to execute
        Returns:
            HandlerResponse
        """
        try:
            # Get the table name from the FROM clause
            table_name = query.from_table.parts[-1]
            
            # Handle different table types
            if table_name == 'clusters':
                clusters = self.connection.list_clusters()
                return Response(RESPONSE_TYPE.TABLE, data_frame=pd.DataFrame(clusters))
            elif table_name == 'services':
                services = self.connection.list_services()
                return Response(RESPONSE_TYPE.TABLE, data_frame=pd.DataFrame(services))
            elif table_name == 'tasks':
                tasks = self.connection.list_tasks()
                return Response(RESPONSE_TYPE.TABLE, data_frame=pd.DataFrame(tasks))
            else:
                return Response(RESPONSE_TYPE.ERROR, error_message=f"Unknown table: {table_name}")
        except Exception as e:
            logger.error(f'Error executing SELECT query: {e}!')
            return Response(RESPONSE_TYPE.ERROR, error_message=str(e))

    def native_query(self, query: str) -> Response:
        """
        Receive raw query and act upon it somehow.
        Args:
            query (str): query in native format
        Returns:
            HandlerResponse
        """
        if not self.is_connected:
            self.connect()

        try:
            result = self.connection.execute_command(query)
            if 'error' in result:
                return Response(RESPONSE_TYPE.ERROR, error_message=result['error'])
            return Response(RESPONSE_TYPE.TABLE, data_frame=pd.DataFrame(result))
        except Exception as e:
            logger.error(f'Error running query: {query} on ECS: {e}!')
            return Response(RESPONSE_TYPE.ERROR, error_message=str(e))

    def query(self, query: ASTNode) -> Response:
        """
        Receive query as AST (abstract syntax tree) and act upon it somehow.
        Args:
            query (ASTNode): sql query represented as AST. May be any kind
                of query: SELECT, INSERT, DELETE, etc
        Returns:
            HandlerResponse
        """
        if not self.is_connected:
            self.connect()

        try:
            if isinstance(query, Select):
                return self._handle_select(query)
            else:
                return Response(RESPONSE_TYPE.ERROR, error_message=f"Query type {type(query)} not supported")
        except Exception as e:
            logger.error(f'Error running query: {query} on ECS: {e}!')
            return Response(RESPONSE_TYPE.ERROR, error_message=str(e))

    def get_tables(self) -> Response:
        """
        Return list of entities that will be accessible as tables.
        Returns:
            HandlerResponse
        """
        if not self.is_connected:
            self.connect()

        try:
            # Define the available "tables" in ECS
            tables = [
                {
                    'name': 'clusters',
                    'description': 'List of ECS clusters'
                },
                {
                    'name': 'services',
                    'description': 'List of services in the cluster'
                },
                {
                    'name': 'tasks',
                    'description': 'List of tasks in the cluster'
                }
            ]
            return Response(RESPONSE_TYPE.TABLE, data_frame=pd.DataFrame(tables))
        except Exception as e:
            logger.error(f'Error getting tables from ECS: {e}!')
            return Response(RESPONSE_TYPE.ERROR, error_message=str(e))

    def get_columns(self, table_name: str) -> Response:
        """
        Returns a list of entity columns.
        Args:
            table_name (str): name of one of tables returned by self.get_tables()
        Returns:
            HandlerResponse
        """
        if not self.is_connected:
            self.connect()

        try:
            # Define columns for each table type
            columns = {
                'clusters': [
                    {'name': 'clusterArn', 'type': 'string'},
                    {'name': 'clusterName', 'type': 'string'},
                    {'name': 'status', 'type': 'string'},
                    {'name': 'activeServicesCount', 'type': 'integer'},
                    {'name': 'runningTasksCount', 'type': 'integer'}
                ],
                'services': [
                    {'name': 'serviceArn', 'type': 'string'},
                    {'name': 'serviceName', 'type': 'string'},
                    {'name': 'status', 'type': 'string'},
                    {'name': 'desiredCount', 'type': 'integer'},
                    {'name': 'runningCount', 'type': 'integer'}
                ],
                'tasks': [
                    {'name': 'taskArn', 'type': 'string'},
                    {'name': 'taskDefinition', 'type': 'string'},
                    {'name': 'status', 'type': 'string'},
                    {'name': 'startedAt', 'type': 'datetime'},
                    {'name': 'stoppedAt', 'type': 'datetime'}
                ]
            }

            if table_name not in columns:
                return Response(RESPONSE_TYPE.ERROR, error_message=f"Unknown table: {table_name}")

            return Response(RESPONSE_TYPE.TABLE, data_frame=pd.DataFrame(columns[table_name]))
        except Exception as e:
            logger.error(f'Error getting columns for table {table_name} from ECS: {e}!')
            return Response(RESPONSE_TYPE.ERROR, error_message=str(e)) 