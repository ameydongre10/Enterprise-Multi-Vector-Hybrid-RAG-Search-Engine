class AsyncTaskTracker:
    def __init__(self):
        self._tasks = {}

    def create_task(self, task_id: str, document_id: str):
        self._tasks[task_id] = {
            "task_id": task_id, "document_id": document_id, "status": "PENDING",
            "progress": 5, "message": "Task queued...", "error": None
        }

    def update_task(self, task_id: str, status: str, progress: int, message: str, error: str = None):
        if task_id in self._tasks:
            self._tasks[task_id].update({"status": status, "progress": progress, "message": message, "error": error})

    def get_task(self, task_id: str):
        return self._tasks.get(task_id, {"task_id": task_id, "status": "UNKNOWN", "progress": 0, "message": "Task ID not found.", "error": None})

task_tracker = AsyncTaskTracker()
