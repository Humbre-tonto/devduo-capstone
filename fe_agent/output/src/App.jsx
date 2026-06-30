import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom/client';

const API_BASE_URL = 'http://localhost:8000';

function App() {
    const [todos, setTodos] = useState([]);
    const [newTodoTitle, setNewTodoTitle] = useState('');
    const [newTodoDescription, setNewTodoDescription] = useState('');

    useEffect(() => {
        fetchTodos();
    }, []);

    const fetchTodos = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/todos`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            setTodos(data);
        } catch (error) {
            console.error("Error fetching todos:", error);
        }
    };

    const addTodo = async (e) => {
        e.preventDefault();
        if (!newTodoTitle.trim()) return;

        try {
            const response = await fetch(`${API_BASE_URL}/todos`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    title: newTodoTitle,
                    description: newTodoDescription
                }),
            });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const newTodo = await response.json();
            setTodos([...todos, newTodo]);
            setNewTodoTitle('');
            setNewTodoDescription('');
        } catch (error) {
            console.error("Error adding todo:", error);
        }
    };

    const toggleTodoComplete = async (id, currentCompletedStatus) => {
        const todoToUpdate = todos.find(todo => todo.id === id);
        if (!todoToUpdate) return;

        try {
            const response = await fetch(`${API_BASE_URL}/todos/${id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    title: todoToUpdate.title,
                    description: todoToUpdate.description,
                    completed: !currentCompletedStatus
                }),
            });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const updatedTodo = await response.json();
            setTodos(todos.map((todo) =>
                todo.id === id ? updatedTodo : todo
            ));
        } catch (error) {
            console.error("Error toggling todo status:", error);
        }
    };

    const deleteTodo = async (id) => {
        try {
            const response = await fetch(`${API_BASE_URL}/todos/${id}`, {
                method: 'DELETE',
            });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            // Assuming successful deletion, remove from UI
            setTodos(todos.filter((todo) => todo.id !== id));
        } catch (error) {
            console.error("Error deleting todo:", error);
        }
    };

    return (
        <div style={{ fontFamily: 'Arial, sans-serif', maxWidth: '600px', margin: '20px auto', padding: '20px', border: '1px solid #eee', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
            <h1 style={{ textAlign: 'center', color: '#333' }}>TODO App</h1>

            <form onSubmit={addTodo} style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '20px' }}>
                <input
                    type="text"
                    placeholder="New todo title"
                    value={newTodoTitle}
                    onChange={(e) => setNewTodoTitle(e.target.value)}
                    style={{ padding: '10px', border: '1px solid #ddd', borderRadius: '4px' }}
                />
                <textarea
                    placeholder="New todo description (optional)"
                    value={newTodoDescription}
                    onChange={(e) => setNewTodoDescription(e.target.value)}
                    rows="3"
                    style={{ padding: '10px', border: '1px solid #ddd', borderRadius: '4px', resize: 'vertical' }}
                ></textarea>
                <button type="submit" style={{ padding: '10px 15px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>Add Todo</button>
            </form>

            <ul style={{ listStyle: 'none', padding: 0 }}>
                {todos.map((todo) => (
                    <li key={todo.id} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 0', borderBottom: '1px solid #eee' }}>
                        <div style={{ display: 'flex', alignItems: 'center', flexGrow: 1 }}>
                            <input
                                type="checkbox"
                                checked={todo.completed}
                                onChange={() => toggleTodoComplete(todo.id, todo.completed)}
                                style={{ marginRight: '10px', transform: 'scale(1.2)' }}
                            />
                            <span style={{ textDecoration: todo.completed ? 'line-through' : 'none', color: todo.completed ? '#888' : '#333' }}>
                                <strong>{todo.title}</strong>
                                {todo.description && <p style={{ margin: '5px 0 0 0', fontSize: '0.9em', color: '#666' }}>{todo.description}</p>}
                            </span>
                        </div>
                        <button
                            onClick={() => deleteTodo(todo.id)}
                            style={{ padding: '8px 12px', backgroundColor: '#dc3545', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
                        >
                            Delete
                        </button>
                    </li>
                ))}
            </ul>
        </div>
    );
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
    <React.StrictMode>
        <App />
    </React.StrictMode>
);
