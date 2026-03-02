class TestHealthcheck:
    def test_healthcheck_returns_200(self, test_client):
        response = test_client.get("/api/v1/healthcheck")
        assert response.status_code == 200

    def test_healthcheck_json_content(self, test_client):
        response = test_client.get("/api/v1/healthcheck")
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "agent-ia-echecs"
