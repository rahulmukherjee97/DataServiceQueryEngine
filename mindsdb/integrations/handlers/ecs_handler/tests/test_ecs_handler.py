import pytest
import json
import threading
import time
from datetime import datetime
from unittest.mock import MagicMock, patch

from mindsdb_sql.parser.ast import Identifier, Select, Star, BinaryOperation, Constant
from mindsdb.integrations.handlers.ecs_handler.ecs_handler import ECSHandler
from mindsdb.integrations.libs.response import RESPONSE_TYPE
from .mock_ecs_server import start_server


HANDLER_KWARGS = {
    "connection_data": {
        "url": "http://localhost:5000",
        "tenant": "test_tenant",
        "username": "test_user",
        "password": "test_password",
        "organization_unit": "Default"
    }
}

expected_columns = [
    "id", "name", "description", "type", "value",
    "createdAt", "updatedAt", "createdBy", "updatedBy",
    "organizationUnitId", "isDeleted"
]


def load_test_data():
    """Load test data from seed file"""
    with open("mindsdb/integrations/handlers/ecs_handler/tests/seed.json", "r") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def mock_server():
    """Start mock server in a separate thread"""
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    time.sleep(1)  # Wait for server to start
    yield
    # Server will be automatically stopped when the thread is killed


@pytest.fixture(scope="module")
def handler(mock_server):
    """Create a handler instance for testing"""
    handler = ECSHandler("ecs_handler", **HANDLER_KWARGS)
    yield handler


def check_valid_response(res):
    """Helper function to check response validity"""
    if res.resp_type == RESPONSE_TYPE.TABLE:
        assert res.data_frame is not None, "expected to have some data, but got None"
    assert res.error_code == 0, f"expected to have zero error_code, but got {res.error_code}"
    assert res.error_message is None, f"expected to have None in error message, but got {res.error_message}"


class TestECSConnection:
    def test_connect(self, handler):
        """Test connection to ECS"""
        res = handler.connect()
        assert res.success is True, "connection error"

    def test_check_connection(self, handler):
        """Test connection check"""
        res = handler.check_connection()
        assert res.success is True, res.error_message

    def test_disconnect(self, handler):
        """Test disconnection"""
        handler.disconnect()
        assert handler.is_connected is False, "failed to disconnect"

    def test_missing_required_params(self):
        """Test initialization with missing required parameters"""
        with pytest.raises(ValueError) as exc_info:
            ECSHandler("ecs_handler", connection_data={})
        assert "Missing required connection parameters" in str(exc_info.value)


class TestECSQuery:
    def test_native_query(self, handler):
        """Test native query execution"""
        query = "list-contexts"
        response = handler.native_query(query)
        check_valid_response(response)
        assert "id" in response.data_frame.columns, f"expected to get 'id' column in response:\n{response.data_frame}"

    def test_select_query(self, handler):
        """Test SELECT query execution"""
        query = Select(
            targets=[Star()],
            from_table=Identifier(parts=["contexts"])
        )
        res = handler.query(query)
        check_valid_response(res)
        assert len(res.data_frame) > 0, "expected to have some rows in response"

    def test_select_with_filter(self, handler):
        """Test SELECT query with WHERE clause"""
        query = Select(
            targets=[Star()],
            from_table=Identifier(parts=["contexts"]),
            where=BinaryOperation(
                op='=',
                args=[
                    Identifier(parts=["type"]),
                    Constant("String")
                ]
            )
        )
        res = handler.query(query)
        check_valid_response(res)
        assert all(res.data_frame["type"] == "String"), "expected all rows to have type 'String'"

    def test_get_context_by_id(self, handler):
        """Test getting a specific context by ID"""
        query = "get-context 1"
        response = handler.native_query(query)
        check_valid_response(response)
        assert len(response.data_frame) == 1, "expected exactly one row"
        assert response.data_frame.iloc[0]["id"] == "1", "expected context with ID 1"

    def test_create_context(self, handler):
        """Test creating a new context"""
        query = 'create-context {"name": "New Context", "type": "String", "value": "new value"}'
        response = handler.native_query(query)
        check_valid_response(response)
        assert response.data_frame.iloc[0]["name"] == "New Context"

    def test_update_context(self, handler):
        """Test updating an existing context"""
        query = 'update-context 1 {"name": "Updated Context", "value": "updated value"}'
        response = handler.native_query(query)
        check_valid_response(response)
        assert response.data_frame.iloc[0]["name"] == "Updated Context"

    def test_delete_context(self, handler):
        """Test deleting a context"""
        query = "delete-context 1"
        response = handler.native_query(query)
        check_valid_response(response)
        assert response.data_frame.iloc[0]["success"] is True


class TestECSTables:
    def test_get_tables(self, handler):
        """Test getting available tables"""
        res = handler.get_tables()
        check_valid_response(res)
        tables = res.data_frame["name"].tolist()
        assert "contexts" in tables, f"expected to have 'contexts' table in the db but got: {tables}"

    def test_get_columns(self, handler):
        """Test getting columns for a table"""
        res = handler.get_columns("contexts")
        check_valid_response(res)
        columns = res.data_frame["name"].tolist()
        assert set(columns) == set(expected_columns), f"expected columns {expected_columns}, but got {columns}"

    def test_get_columns_invalid_table(self, handler):
        """Test getting columns for non-existent table"""
        res = handler.get_columns("invalid_table")
        assert res.resp_type == RESPONSE_TYPE.ERROR
        assert "Unknown table" in res.error_message


class TestECSErrorHandling:
    def test_invalid_table(self, handler):
        """Test handling of invalid table name"""
        query = Select(
            targets=[Star()],
            from_table=Identifier(parts=["invalid_table"])
        )
        res = handler.query(query)
        assert res.resp_type == RESPONSE_TYPE.ERROR, "expected error response for invalid table"
        assert "Unknown table" in res.error_message, "expected error message about unknown table"

    def test_invalid_query(self, handler):
        """Test handling of invalid query"""
        query = "invalid-command"
        res = handler.native_query(query)
        assert res.resp_type == RESPONSE_TYPE.ERROR, "expected error response for invalid query"
        assert "error" in res.error_message.lower(), "expected error message for invalid query"

    def test_invalid_json_in_create(self, handler):
        """Test handling of invalid JSON in create context"""
        query = "create-context invalid-json"
        res = handler.native_query(query)
        assert res.resp_type == RESPONSE_TYPE.ERROR
        assert "error" in res.error_message.lower()

    def test_missing_id_in_update(self, handler):
        """Test handling of missing ID in update context"""
        query = "update-context"
        res = handler.native_query(query)
        assert res.resp_type == RESPONSE_TYPE.ERROR
        assert "error" in res.error_message.lower() 