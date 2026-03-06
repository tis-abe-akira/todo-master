from datetime import datetime
import logging
import os
import uuid

from .local_store import LocalStore
from .models import CreateTodo, Todo, UpdateTodo

logger = logging.getLogger("todo_app")


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
    logger.info("create: Todo created id=%s title=%r", todo.id, todo.title)
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
            logger.info("update: Todo updated id=%s", todo_id)
            return todos[i]
    logger.warning("update: Todo not found id=%s", todo_id)
    raise KeyError(f"Todo with id '{todo_id}' not found")


def delete_todo(store: LocalStore, todo_id: str) -> None:
    """指定 id の Todo を削除して永続化する。存在しない id は KeyError を送出する。"""
    todos = store.load()
    new_todos = [item for item in todos if item["id"] != todo_id]
    if len(new_todos) == len(todos):
        logger.warning("delete: Todo not found id=%s", todo_id)
        raise KeyError(f"Todo with id '{todo_id}' not found")
    store.save(new_todos)
    logger.info("delete: Todo deleted id=%s", todo_id)
    return None


def create_app(store_path: str):
    # Import FastAPI lazily to avoid hard dependency at module import time in tests
    from fastapi import FastAPI, Request
    from fastapi.responses import JSONResponse

    app = FastAPI()
    app.state.store = LocalStore(store_path)

    # 5.3: 永続化失敗（IOError/OSError）を 500 + 再試行ヒント付きで返す
    @app.exception_handler(IOError)
    async def persistence_error_handler(request: Request, exc: IOError):
        logger.error("persistence error: %s", exc)
        return JSONResponse(
            status_code=500,
            content={
                "detail": "データの保存に失敗しました。時間をおいて再試行してください。(retry later)"
            },
        )

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


# uvicorn app.main:app で直接起動できるようにモジュールレベルのインスタンスを作成
app = create_app(os.path.join(os.path.dirname(__file__), "..", "todos.json"))
