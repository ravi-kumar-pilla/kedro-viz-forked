from unittest import mock

import pytest
from fastapi.testclient import TestClient

from kedro_viz.api import apps


class TestIndexEndpoint:
    def test_index(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert "heap" not in response.text
        assert "checkReloadStatus" not in response.text

    @mock.patch("kedro_viz.integrations.kedro.telemetry.get_heap_app_id")
    @mock.patch("kedro_viz.integrations.kedro.telemetry.get_heap_identity")
    def test_heap_enabled(
        self, mock_get_heap_identity, mock_get_heap_app_id, client, tmpdir
    ):
        mock_get_heap_app_id.return_value = "my_heap_app"
        mock_get_heap_identity.return_value = "my_heap_identity"
        response = client.get("/")
        assert response.status_code == 200
        assert 'heap.load("my_heap_app")' in response.text
        assert 'heap.identify("my_heap_identity")' in response.text


@pytest.fixture
def example_autoreload_api():
    yield apps.create_api_app_from_project(mock.MagicMock(), autoreload=True)


class TestReloadEndpoint:
    def test_autoreload_script_added_to_index(self, example_autoreload_api):
        client = TestClient(example_autoreload_api)
        response = client.get("/")
        assert response.status_code == 200
        assert "checkReloadStatus" in response.text

    def test_reload_endpoint_return_400_when_header_not_set(
        self, example_autoreload_api
    ):
        client = TestClient(example_autoreload_api)
        response = client.get("/api/reload")
        assert response.status_code == 400

    @mock.patch("kedro_viz.api.apps._create_etag")
    def test_reload_endpoint_return_304_when_content_has_not_changed(
        self, patched_create_etag
    ):
        patched_create_etag.return_value = "old etag"
        api = apps.create_api_app_from_project(mock.MagicMock(), autoreload=True)

        client = TestClient(api)

        # if the client sends an If-None-Match header with the same value as the etag value
        # on the server, the server should return a 304
        response = client.get("/api/reload", headers={"If-None-Match": "old etag"})
        assert response.status_code == 304

        # when the etag has changed, the server will return a 200
        response = client.get("/api/reload", headers={"If-None-Match": "new etag"})
        assert response.status_code == 200
