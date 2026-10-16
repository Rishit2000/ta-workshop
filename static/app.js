document.addEventListener('DOMContentLoaded', fetchTasks);

const validPriorities = ['Low', 'Medium', 'High'];

async function fetchTasks() {
    const response = await fetch('/api/tasks');
    const tasks = await response.json();
    const taskList = document.getElementById('task-list');
    taskList.innerHTML = '';

    tasks.forEach(task => {
        const priority = validPriorities.includes(task.priority)
            ? task.priority
            : 'Medium';
        const li = document.createElement('li');
        const details = document.createElement('div');
        const title = document.createElement('span');
        const priorityLabel = document.createElement('span');
        const deleteButton = document.createElement('button');

        details.className = 'task-details';
        title.className = 'task-title';
        title.textContent = task.title;
        priorityLabel.className = `priority priority-${priority.toLowerCase()}`;
        priorityLabel.textContent = priority;
        deleteButton.className = 'delete-btn';
        deleteButton.textContent = 'Delete';
        deleteButton.addEventListener('click', () => deleteTask(task.id));

        details.appendChild(title);
        details.appendChild(priorityLabel);
        li.appendChild(details);
        li.appendChild(deleteButton);
        taskList.appendChild(li);
    });
}

async function addTask() {
    const titleInput = document.getElementById('task-title');
    const priorityInput = document.getElementById('task-priority');
    const title = titleInput.value.trim();
    const priority = validPriorities.includes(priorityInput.value)
        ? priorityInput.value
        : 'Medium';

    if (!title) return;

    await fetch('/api/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, priority })
    });

    titleInput.value = '';
    priorityInput.value = 'Medium';
    fetchTasks();
}

async function deleteTask(id) {
    await fetch(`/api/tasks/${id}`, {
        method: 'DELETE'
    });
    fetchTasks();
}
