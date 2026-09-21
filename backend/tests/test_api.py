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

def test_child_delete_and_questionnaire(client):
    # 1. Create Child 1 and Child 2
    c1 = client.post("/api/children", json={"external_id": "DEL-C-01", "age_months": 24, "gender": "Male"}).json()
    c2 = client.post("/api/children", json={"external_id": "DEL-C-02", "age_months": 30, "gender": "Female"}).json()
    
    c1_id = c1["id"]
    c2_id = c2["id"]
    assert c1["profile_number"] is not None
    assert c2["profile_number"] > c1["profile_number"]
    
    # 2. Add Parent Questionnaire for C1
    q_data = {
        "developmental_context": {
            "school_setting": "Pre-K",
            "primary_communication": "Verbal",
            "home_languages": "English"
        },
        "communication": {
            "communicate_needs": "Always",
            "communication_mode": "Speech"
        },
        "social_interaction": {
            "initiate_interaction": "Frequently",
            "respond_name": "Consistently"
        },
        "sensory_context": ["Loud sounds"],
        "parent_observations": "Enjoys music and building blocks."
    }
    q_res = client.post(f"/api/children/{c1_id}/questionnaire", json=q_data)
    assert q_res.status_code == 200
    q_body = q_res.json()
    assert q_body["child_id"] == c1_id
    assert q_body["parent_observations"] == "Enjoys music and building blocks."
    
    # 3. GET questionnaire for C1
    get_q = client.get(f"/api/children/{c1_id}/questionnaire")
    assert get_q.status_code == 200
    assert get_q.json()["developmental_context"]["school_setting"] == "Pre-K"
    
    # 4. Check 404 for uncompleted questionnaire (C2)
    get_q2 = client.get(f"/api/children/{c2_id}/questionnaire")
    assert get_q2.status_code == 404
    
    # 5. Delete Child 1
    del_res = client.delete(f"/api/children/{c1_id}")
    assert del_res.status_code == 204
    
    # 6. Verify Child 1 is gone (404)
    get_c1 = client.get(f"/api/children/{c1_id}")
    assert get_c1.status_code == 404
    
    # 7. Verify Child 2 remains intact
    get_c2 = client.get(f"/api/children/{c2_id}")
    assert get_c2.status_code == 200
    assert get_c2.json()["profile_number"] == c2["profile_number"]

    # 8. Delete non-existent child (404)
    del_fake = client.delete(f"/api/children/{c1_id}")
    assert del_fake.status_code == 404
