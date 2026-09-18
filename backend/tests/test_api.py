def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "NeuroTrack AI"

def test_child_crud(client):
    # 1. Create child
    child_data = {
        "external_id": "TEST-CHILD-01",
        "age_months": 36,
        "gender": "Male",
        "notes": "Test subject profile"
    }
    create_res = client.post("/api/children", json=child_data)
    assert create_res.status_code == 201
    child = create_res.json()
    assert child["external_id"] == "TEST-CHILD-01"
    child_id = child["id"]

    # 2. Get list
    list_res = client.get("/api/children")
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1

    # 3. Get single
    get_res = client.get(f"/api/children/{child_id}")
    assert get_res.status_code == 200
    assert get_res.json()["external_id"] == "TEST-CHILD-01"

def test_tasks_list(client):
    response = client.get("/api/tasks")
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) >= 2
    codes = [t["code"] for t in tasks]
    assert "joint_attention" in codes
    assert "imitation" in codes

def test_session_lifecycle(client):
    # Create Child
    c_res = client.post("/api/children", json={"external_id": "TEST-C-02", "age_months": 42, "gender": "Female"})
    child_id = c_res.json()["id"]

    # Get Tasks
    t_res = client.get("/api/tasks")
    task_id = t_res.json()[0]["id"]

    # Create Session
    s_res = client.post("/api/sessions", json={"child_id": child_id, "task_id": task_id, "notes": "Session test"})
    assert s_res.status_code == 201
    session = s_res.json()
    assert session["status"] == "CREATED"
