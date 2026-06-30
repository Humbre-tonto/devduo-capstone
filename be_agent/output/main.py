from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory database
todos_db: Dict[str, Dict] = {}

class TodoItem(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    completed: bool = False

class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

@app.post("/todos", response_model=TodoItem, status_code=201)
async def create_todo(todo: TodoCreate):
    todo_id = str(uuid.uuid4())
    new_todo = TodoItem(id=todo_id, title=todo.title, description=todo.description)
    todos_db[todo_id] = new_todo.dict()
    return new_todo

@app.get("/todos", response_model=List[TodoItem])
async def get_all_todos():
    return list(todos_db.values())

@app.get("/todos/{todo_id}", response_model=TodoItem)
async def get_todo(todo_id: str):
    if todo_id not in todos_db:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todos_db[todo_id]

@app.put("/todos/{todo_id}", response_model=TodoItem)
async def update_todo(todo_id: str, todo_update: TodoUpdate):
    if todo_id not in todos_db:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    current_todo_data = todos_db[todo_id]
    update_data = todo_update.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        current_todo_data[key] = value
    
    todos_db[todo_id] = current_todo_data
    return TodoItem(**current_todo_data)

@app.delete("/todos/{todo_id}", status_code=204)
async def delete_todo(todo_id: str):
    if todo_id not in todos_db:
        raise HTTPException(status_code=404, detail="Todo not found")
    del todos_db[todo_id]
