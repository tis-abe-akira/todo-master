from datetime import datetime
import uuid

from .local_store import LocalStore
from .models import CreateTodo, Todo, UpdateTodo


def _now_iso() -> str:
    # UTC ISO8601 with Z
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def create_and_persist_todo(store: LocalStore, payload: CreateTodo) -> dict:
    """Create a Todo object from payload, persist it to store, and return dict."""
    todos = store.load()
    now = _now_iso()
    todo = Todo(
        id=str(uuid.uuid4()),
        title=payload.title,
        description=payload.description,
        completed=False,
        created_at=now,
        updated_at=now,
    )
    todos.append(todo.model_dump())
    store.save(todos)
    return todo.model_dump()


def list_todos(store: LocalStore) -> list:
    """LocalStore から全 Todo を読み込んでリストで返す。"""
    return store.load()


def update_todo(store: LocalStore, todo_id: str, payload: UpdateTodo) -> dict:
    """指定 id の Todo を部分更新して永続化し、更新後の dict を返す。
    存在しない id の場合は KeyError を送出する。
    """
    todos = store.load()
    for i, item in enumerate(todos):
        if item["id"] == todo_id:
            update_data = payload.model_dump(exclude_unset=True)
            todos[i].update(update_data)
            todos[i]["updated_at"] = _now_iso()
            store.save(todos)
            return todos[i]
    raise KeyError(f"Todo with id '{todo_id}' not found")


def delete_todo(store: LocalStore, todo_id: str) -> None:
    """指定 id の Todo を削除して永続化する。存在しない id は KeyError を送出する。"""
    todos = store.load()
    new_todos = [item for item in todos if item["id"] != todo_id]
    if len(new_todos) == len(todos):
        raise KeyError(f"Todo with id '{todo_id}' not found")
    store.save(new_todos)
    return None


def create_app(store_path: str):
    # Import FastAPI lazily to avoid hard dependency at module import time in tests
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse

    app = FastAPI()
    app.state.store = LocalStore(store_path)

    @app.get("/api/todos", response_model=list[Todo], status_code=200)
    def get_todos():
        return list_todos(app.state.store)

    @app.put("/api/todos/{todo_id}", response_model=Todo, status_code=200)
    def put_todo(todo_id: str, payload: UpdateTodo):
        from fastapi import HTTPException

        try:
            return update_todo(app.state.store, todo_id, payload)
        except KeyError:
            raise HTTPException(status_code=404, detail=f"Todo '{todo_id}' not found")

    @app.delete("/api/todos/{todo_id}", status_code=204)
    def remove_todo(todo_id: str):
        from fastapi import HTTPException
        from fastapi.responses import Response

        try:
            delete_todo(app.state.store, todo_id)
            return Response(status_code=204)
        except KeyError:
            raise HTTPException(status_code=404, detail=f"Todo '{todo_id}' not found")

    @app.post("/api/todos", response_model=Todo, status_code=201)
    def create_todo(payload: CreateTodo):
        todo_dict = create_and_persist_todo(app.state.store, payload)
        return JSONResponse(content=todo_dict, status_code=201)

    return app
