class TestCreateTask:
    def test_create_task_returns_201_and_sets_defaults(self, client):
        response = client.post("/tasks", json={"title": "Buy milk"})
        assert response.status_code == 201
        body = response.json()
        assert body["title"] == "Buy milk"
        assert body["status"] == "ToDo"
        assert body["priority"] == "Medium"
        assert "id" in body

    def test_create_task_rejects_blank_title(self, client):
        response = client.post("/tasks", json={"title": "   "})
        assert response.status_code == 422

    def test_create_task_rejects_missing_title(self, client):
        response = client.post("/tasks", json={"description": "no title"})
        assert response.status_code == 422

    def test_create_task_rejects_unknown_field(self, client):
        response = client.post("/tasks", json={"title": "Test", "extra_field": "nope"})
        assert response.status_code == 422

    def test_create_task_rejects_invalid_status(self, client):
        response = client.post("/tasks", json={"title": "Test", "status": "Blocked"})
        assert response.status_code == 422


class TestListTasks:
    def test_list_tasks_empty_returns_200_and_empty_list(self, client):
        response = client.get("/tasks")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_tasks_returns_created_tasks(self, client, created_task):
        response = client.get("/tasks")
        assert response.status_code == 200
        body = response.json()
        assert len(body) == 1
        assert body[0]["id"] == created_task["id"]

    def test_filter_by_status_returns_matching_only(self, client):
        client.post("/tasks", json={"title": "A", "status": "ToDo"})
        client.post("/tasks", json={"title": "B", "status": "InProgress"})

        response = client.get("/tasks", params={"status": "InProgress"})
        assert response.status_code == 200
        body = response.json()
        assert len(body) == 1
        assert body[0]["title"] == "B"

    def test_filter_by_priority_returns_matching_only(self, client):
        client.post("/tasks", json={"title": "A", "priority": "Low"})
        client.post("/tasks", json={"title": "B", "priority": "High"})

        response = client.get("/tasks", params={"priority": "High"})
        assert response.status_code == 200
        body = response.json()
        assert len(body) == 1
        assert body[0]["title"] == "B"

    def test_filter_with_no_matches_returns_200_empty_list(self, client, created_task):
        response = client.get("/tasks", params={"priority": "Low"})
        assert response.status_code == 200
        assert response.json() == []

    def test_filter_invalid_status_value_returns_422(self, client):
        response = client.get("/tasks", params={"status": "NotAStatus"})
        assert response.status_code == 422


class TestGetTask:
    def test_get_task_returns_task(self, client, created_task):
        response = client.get(f"/tasks/{created_task['id']}")
        assert response.status_code == 200
        assert response.json()["id"] == created_task["id"]

    def test_get_task_missing_returns_404(self, client):
        response = client.get("/tasks/does-not-exist")
        assert response.status_code == 404


class TestUpdateTask:
    def test_partial_update_changes_only_given_fields(self, client, created_task):
        response = client.patch(f"/tasks/{created_task['id']}", json={"priority": "Low"})
        assert response.status_code == 200
        body = response.json()
        assert body["priority"] == "Low"
        assert body["title"] == created_task["title"]

    def test_update_missing_task_returns_404(self, client):
        response = client.patch("/tasks/does-not-exist", json={"title": "New"})
        assert response.status_code == 404

    def test_update_rejects_blank_title(self, client, created_task):
        response = client.patch(f"/tasks/{created_task['id']}", json={"title": "   "})
        assert response.status_code == 422

    def test_valid_status_transition_todo_to_in_progress(self, client, created_task):
        response = client.patch(
            f"/tasks/{created_task['id']}", json={"status": "InProgress"}
        )
        assert response.status_code == 200
        assert response.json()["status"] == "InProgress"

    def test_done_cannot_move_back_to_todo(self, client, created_task):
        client.patch(f"/tasks/{created_task['id']}", json={"status": "Done"})
        response = client.patch(f"/tasks/{created_task['id']}", json={"status": "ToDo"})
        assert response.status_code == 422

    def test_done_cannot_move_back_to_in_progress(self, client, created_task):
        client.patch(f"/tasks/{created_task['id']}", json={"status": "Done"})
        response = client.patch(
            f"/tasks/{created_task['id']}", json={"status": "InProgress"}
        )
        assert response.status_code == 422


class TestDueDateAndOverdue:
    def test_create_task_with_valid_due_date(self, client):
        response = client.post(
            "/tasks", json={"title": "Pay bill", "due_date": "2030-01-01"}
        )
        assert response.status_code == 201
        assert response.json()["due_date"] == "2030-01-01"

    def test_create_task_rejects_invalid_due_date_format(self, client):
        response = client.post(
            "/tasks", json={"title": "Pay bill", "due_date": "not-a-date"}
        )
        assert response.status_code == 422

    def test_future_due_date_is_not_overdue(self, client):
        response = client.post(
            "/tasks", json={"title": "Future task", "due_date": "2099-01-01"}
        )
        assert response.json()["is_overdue"] is False

    def test_past_due_date_is_overdue(self, client):
        response = client.post(
            "/tasks", json={"title": "Late task", "due_date": "2000-01-01"}
        )
        assert response.json()["is_overdue"] is True

    def test_done_task_with_past_due_date_is_not_overdue(self, client):
        create = client.post(
            "/tasks", json={"title": "Late but done", "due_date": "2000-01-01"}
        )
        task_id = create.json()["id"]
        response = client.patch(f"/tasks/{task_id}", json={"status": "Done"})
        assert response.json()["is_overdue"] is False

    def test_task_with_no_due_date_is_not_overdue(self, client, created_task):
        assert created_task["is_overdue"] is False

    def test_update_due_date(self, client, created_task):
        response = client.patch(
            f"/tasks/{created_task['id']}", json={"due_date": "2030-06-15"}
        )
        assert response.status_code == 200
        assert response.json()["due_date"] == "2030-06-15"

    def test_filter_overdue_true_returns_only_overdue(self, client):
        client.post("/tasks", json={"title": "Late", "due_date": "2000-01-01"})
        client.post("/tasks", json={"title": "Future", "due_date": "2099-01-01"})
        client.post("/tasks", json={"title": "No date"})

        response = client.get("/tasks", params={"overdue": "true"})
        assert response.status_code == 200
        body = response.json()
        assert len(body) == 1
        assert body[0]["title"] == "Late"


class TestTags:
    def test_create_task_with_tags(self, client):
        response = client.post(
            "/tasks", json={"title": "Fix bug", "tags": ["backend", "urgent"]}
        )
        assert response.status_code == 201
        assert response.json()["tags"] == ["backend", "urgent"]

    def test_create_task_defaults_to_empty_tags(self, client, created_task):
        assert created_task["tags"] == []

    def test_create_task_rejects_empty_tag(self, client):
        response = client.post(
            "/tasks", json={"title": "Fix bug", "tags": ["backend", "   "]}
        )
        assert response.status_code == 422

    def test_create_task_trims_tag_whitespace(self, client):
        response = client.post(
            "/tasks", json={"title": "Fix bug", "tags": ["  backend  "]}
        )
        assert response.status_code == 201
        assert response.json()["tags"] == ["backend"]

    def test_create_task_deduplicates_tags(self, client):
        response = client.post(
            "/tasks", json={"title": "Fix bug", "tags": ["backend", "backend"]}
        )
        assert response.status_code == 201
        assert response.json()["tags"] == ["backend"]

    def test_create_task_rejects_too_many_tags(self, client):
        response = client.post(
            "/tasks", json={"title": "Fix bug", "tags": [f"tag{i}" for i in range(11)]}
        )
        assert response.status_code == 422

    def test_update_tags_replaces_list(self, client, created_task):
        response = client.patch(
            f"/tasks/{created_task['id']}", json={"tags": ["frontend"]}
        )
        assert response.status_code == 200
        assert response.json()["tags"] == ["frontend"]

    def test_update_without_tags_field_preserves_existing_tags(self, client):
        create = client.post("/tasks", json={"title": "Fix bug", "tags": ["backend"]})
        task_id = create.json()["id"]
        response = client.patch(f"/tasks/{task_id}", json={"priority": "High"})
        assert response.status_code == 200
        assert response.json()["tags"] == ["backend"]

    def test_update_with_empty_tags_list_clears_tags(self, client):
        create = client.post("/tasks", json={"title": "Fix bug", "tags": ["backend"]})
        task_id = create.json()["id"]
        response = client.patch(f"/tasks/{task_id}", json={"tags": []})
        assert response.status_code == 200
        assert response.json()["tags"] == []

    def test_filter_by_tag_returns_matching_only(self, client):
        client.post("/tasks", json={"title": "A", "tags": ["backend"]})
        client.post("/tasks", json={"title": "B", "tags": ["frontend"]})

        response = client.get("/tasks", params={"tag": "backend"})
        assert response.status_code == 200
        body = response.json()
        assert len(body) == 1
        assert body[0]["title"] == "A"

    def test_filter_by_tag_with_no_matches_returns_empty_list(self, client, created_task):
        response = client.get("/tasks", params={"tag": "nonexistent"})
        assert response.status_code == 200
        assert response.json() == []


class TestDeleteTask:
    def test_delete_task_returns_204(self, client, created_task):
        response = client.delete(f"/tasks/{created_task['id']}")
        assert response.status_code == 204

    def test_delete_task_actually_removes_it(self, client, created_task):
        client.delete(f"/tasks/{created_task['id']}")
        response = client.get(f"/tasks/{created_task['id']}")
        assert response.status_code == 404

    def test_delete_missing_task_returns_404(self, client):
        response = client.delete("/tasks/does-not-exist")
        assert response.status_code == 404
