import pytest

import app as app_module


@pytest.fixture
def client():
    """Provide a Flask test client with a clean task list."""
    app_module.tasks = [
        {"id": 1, "title": "Project-1 Report", "priority": "Medium"},
        {"id": 2, "title": "Project-2 MMFs", "priority": "Medium"},
    ]
    app_module.next_id = 3
    app_module.app.config["TESTING"] = True

    with app_module.app.test_client() as test_client:
        yield test_client


def test_index(client):
    """Render the task tracker page."""
    response = client.get("/")

    assert response.status_code == 200
    assert b"Task Tracker" in response.data
    assert b"task-priority" in response.data


def test_get_tasks(client):
    """Return all tasks from the task API."""
    response = client.get("/api/tasks")

    assert response.status_code == 200
    assert response.get_json() == [
        {"id": 1, "title": "Project-1 Report", "priority": "Medium"},
        {"id": 2, "title": "Project-2 MMFs", "priority": "Medium"},
    ]


def test_add_task_success(client):
    """Create a task with its requested priority."""
    response = client.post(
        "/api/tasks",
        json={"title": "Write tests", "priority": "High"},
    )

    assert response.status_code == 201
    assert response.get_json() == {
        "id": 3,
        "title": "Write tests",
        "priority": "High",
    }


def test_add_task_each_priority(client):
    """Accept each supported task priority."""
    for priority in ("Low", "Medium", "High"):
        response = client.post(
            "/api/tasks",
            json={"title": "A task", "priority": priority},
        )

        assert response.status_code == 201
        assert response.get_json()["priority"] == priority


def test_add_task_blank_priority_defaults_to_medium(client):
    """Use Medium when the submitted priority is blank."""
    response = client.post(
        "/api/tasks",
        json={"title": "A task", "priority": ""},
    )

    assert response.status_code == 201
    assert response.get_json()["priority"] == "Medium"


def test_add_task_invalid_priority(client):
    """Reject priorities outside the supported values."""
    response = client.post(
        "/api/tasks",
        json={"title": "A task", "priority": "Urgent"},
    )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "Priority must be Low, Medium, or High",
    }


def test_get_tasks_defaults_legacy_priority(client):
    """Supply Medium for tasks created without a priority."""
    app_module.tasks.append({"id": 3, "title": "Legacy task"})

    response = client.get("/api/tasks")

    assert response.status_code == 200
    assert response.get_json()[-1]["priority"] == "Medium"


def test_add_task_missing_title(client):
    """Reject task creation requests without a title."""
    response = client.post(
        "/api/tasks",
        json={"priority": "Low"},
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "Title is required"}


def test_delete_task(client):
    """Delete a task by its identifier."""
    response = client.delete("/api/tasks/1")

    assert response.status_code == 200
    assert response.get_json() == {"result": "success"}
    assert client.get("/api/tasks").get_json() == [
        {"id": 2, "title": "Project-2 MMFs", "priority": "Medium"},
    ]


def test_frontend_supports_priority_submission_and_display(client):
    """Include priority controls and rendering logic in the frontend."""
    page = client.get("/").get_data(as_text=True)
    script = client.get("/static/app.js").get_data(as_text=True)

    assert 'id="task-priority"' in page
    assert '<option value="Low">Low</option>' in page
    assert '<option value="Medium" selected>Medium</option>' in page
    assert '<option value="High">High</option>' in page
    assert "priority" in script
    assert "DEFAULT_PRIORITY" in script
