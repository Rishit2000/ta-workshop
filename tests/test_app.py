from pathlib import Path

import pytest

import app as app_module


@pytest.fixture
def client(monkeypatch):
    """Provide a client with isolated task data for each test."""
    monkeypatch.setattr(
        app_module,
        "tasks",
        [
            {"id": 1, "title": "Project-1 Report"},
            {"id": 2, "title": "Project-2 MMFs"},
        ],
    )
    monkeypatch.setattr(app_module, "next_id", 3)
    return app_module.app.test_client()


def test_index(client):
    """Render the task tracker page successfully."""
    response = client.get("/")

    assert response.status_code == 200
    assert b"Task Tracker" in response.data


def test_get_tasks_returns_default_priority_for_legacy_tasks(client):
    """Return Medium for tasks that do not have a priority."""
    response = client.get("/api/tasks")

    assert response.status_code == 200
    assert response.get_json() == [
        {
            "id": 1,
            "title": "Project-1 Report",
            "priority": "Medium",
        },
        {
            "id": 2,
            "title": "Project-2 MMFs",
            "priority": "Medium",
        },
    ]


@pytest.mark.parametrize("priority", ["Low", "Medium", "High"])
def test_add_task_supports_all_priorities(client, priority):
    """Create a task with each supported priority."""
    response = client.post(
        "/api/tasks",
        json={"title": "Prioritized task", "priority": priority},
    )

    assert response.status_code == 201
    assert response.get_json() == {
        "id": 3,
        "title": "Prioritized task",
        "priority": priority,
    }

    tasks_response = client.get("/api/tasks")
    assert tasks_response.get_json()[-1]["priority"] == priority


def test_add_task_defaults_missing_priority_to_medium(client):
    """Default a newly created task to Medium when priority is omitted."""
    response = client.post("/api/tasks", json={"title": "Unprioritized task"})

    assert response.status_code == 201
    assert response.get_json()["priority"] == "Medium"


def test_add_task_defaults_invalid_priority_to_medium(client):
    """Default a newly created task to Medium for invalid priority values."""
    response = client.post(
        "/api/tasks",
        json={"title": "Invalid priority task", "priority": "Urgent"},
    )

    assert response.status_code == 201
    assert response.get_json()["priority"] == "Medium"

    tasks_response = client.get("/api/tasks")
    assert tasks_response.get_json()[-1]["priority"] == "Medium"


def test_add_task_missing_title(client):
    """Reject a task creation request without a title."""
    response = client.post("/api/tasks", json={"priority": "High"})

    assert response.status_code == 400
    assert response.get_json() == {"error": "Title is required"}


def test_delete_task(client):
    """Delete a task by its identifier."""
    response = client.delete("/api/tasks/1")

    assert response.status_code == 200
    assert response.get_json() == {"result": "success"}
    assert all(task["id"] != 1 for task in client.get("/api/tasks").get_json())


def test_frontend_has_priority_selector_and_rendering():
    """Verify the frontend submits and displays task priorities."""
    project_root = Path(__file__).resolve().parents[1]
    template = (project_root / "templates" / "index.html").read_text()
    script = (project_root / "static" / "app.js").read_text()

    assert 'id="task-priority"' in template
    assert '<option value="Low">Low</option>' in template
    assert '<option value="Medium" selected>Medium</option>' in template
    assert '<option value="High">High</option>' in template
    assert "JSON.stringify({ title, priority })" in script
    assert "priorityLabel.textContent = priority" in script
