// ============================================================
// task_detail.js — SaaS-Optimized AJAX Logic
// ============================================================

document.addEventListener('DOMContentLoaded', function() {
    // 1. Setup Configuration & CSRF
    const config = document.getElementById('page-config');
    if (!config) return; // Safety exit if not on task detail page

    const TASK_ID = config.dataset.taskId;
    const CSRF_TOKEN = config.dataset.csrf;

    // 2. Task Status AJAX (Todo / Doing / Done)
    document.querySelectorAll('.status-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            fetch(`/task/${this.dataset.id}/status/${this.dataset.status}/`, {
                method: "POST",
                headers: { 'X-CSRFToken': CSRF_TOKEN }
            })
            .then(res => {
                if (res.ok) {
                    // Reload ensures Django re-renders the correct button colors
                    location.reload(); 
                }
            })
            .catch(err => console.error("Status update failed:", err));
        });
    });

    // 3. Quick Access (Pin) AJAX
    document.addEventListener("click", function(e) {
        if (e.target.classList.contains("quick-btn")) {
            const btn = e.target;
            fetch(`/task/${btn.dataset.id}/quick/`, {
                method: "POST",
                headers: { 'X-CSRFToken': CSRF_TOKEN }
            })
            .then(res => res.json())
            .then(data => {
                btn.innerHTML = data.quick ? "★ Pinned" : "☆ Pin";
            });
        }
    });

    // 4. Subtask Toggle AJAX
    document.querySelectorAll('.toggle-subtask').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const textElement = document.getElementById(`subtask-text-${this.dataset.id}`);
            fetch(`/subtask/${this.dataset.id}/toggle/`, {
                method: "POST",
                headers: { 'X-CSRFToken': CSRF_TOKEN }
            })
            .then(res => res.json())
            .then(data => {
                if (data.status === "done") {
                    textElement.classList.add('text-decoration-line-through', 'text-muted');
                } else {
                    textElement.classList.remove('text-decoration-line-through', 'text-muted');
                }
            });
        });
    });

    // 5. Editor.js Initialization with Safety Checks
    const editorElem = document.getElementById('editorjs');
    if (editorElem) {
        let editorData = { blocks: [] };
        try {
            const rawData = document.getElementById('existing-data').value;
            if (rawData && rawData.trim().startsWith('{')) {
                editorData = JSON.parse(rawData);
            }
        } catch (e) {
            console.warn("Starting with clean slate.");
        }

        const editor = new EditorJS({
            holder: 'editorjs',
            placeholder: "Press '/' for commands, or start typing...",
            data: editorData,
            tools: {
                header: window.Header,
                list: window.List || window.EditorjsList,
                checklist: window.Checklist,
                code: window.CodeTool,
                inlineCode: window.InlineCode,
                marker: window.Marker,
                table: window.Table,
                warning: window.Warning,
                delimiter: window.Delimiter,
            }
        });

        // 6. Save Notes AJAX
        const saveBtn = document.getElementById('save-notes-btn');
        if (saveBtn) {
            saveBtn.addEventListener('click', function() {
                saveBtn.innerText = "Saving...";
                editor.save().then((outputData) => {
                    fetch(`/task/${TASK_ID}/update-description/`, {
                        method: "POST",
                        headers: {
                            'X-CSRFToken': CSRF_TOKEN,
                            'Content-Type': 'application/x-www-form-urlencoded',
                        },
                        body: `description=${encodeURIComponent(JSON.stringify(outputData))}`
                    })
                    .then(res => {
                        if (res.ok) {
                            saveBtn.innerText = "Save Notes";
                            const statusText = document.getElementById('save-status');
                            statusText.style.display = 'inline-block';
                            setTimeout(() => statusText.style.display = 'none', 2500);
                        }
                    });
                }).catch(err => {
                    console.error("Save failed:", err);
                    saveBtn.innerText = "Error!";
                });
            });
        }
    }
});