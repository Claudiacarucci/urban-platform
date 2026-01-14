def test_health_check(client):
    """Verifica che il servizio risponda 200 OK"""
    response = client.get('/')
    assert response.status_code == 200
    assert response.json['service'] == "ticket-service"
