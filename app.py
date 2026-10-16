from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

VALID_PRIORITIES = {"Low", "Medium", "High"}
DEFAULT_PRIORITY = "Medium"

tasks = [
    {"id": 1, "title": "Project-1 Report", "priority": DEFAULT_PRIORITY},
    {"id": 2, "title": "Project-2 MMFs", "priority": DEFAULT_PRIORITY},
]
next_id = 3


def get_priority(data):
    """Return a validated task priority with a Medium default."""
    priority = data.get("priority", DEFAULT_PRIORITY)
    if priority is None or (
        isinstance(priority, str) and not priority.strip()
    ):
        return DEFAULT_PRIORITY
    return priority


@app.route("/")
def index():
    """Render the task tracker page."""
    return render_template("index.html")


@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    """Return all tasks, supplying defaults for legacy task data."""
    for task in tasks:
        task.setdefault("priority", DEFAULT_PRIORITY)
    return jsonify(tasks)


@app.route("/api/tasks", methods=["POST"])
def add_task():
    """Validate and create a new task."""
    global next_id
    data = request.get_json()

    if not data or not data.get("title"):
        return jsonify({"error": "Title is required"}), 400

    priority = get_priority(data)
    if not isinstance(priority, str) or priority not in VALID_PRIORITIES:
        return jsonify({
            "error": "Priority must be Low, Medium, or High",
        }), 400

    new_task = {
        "id": next_id,
        "title": data["title"],
        "priority": priority,
    }
    tasks.append(new_task)
    next_id += 1

    return jsonify(new_task), 201


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    """Delete a task by its identifier."""
    global tasks
    tasks = [task for task in tasks if task["id"] != task_id]
    return jsonify({"result": "success"}), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)
