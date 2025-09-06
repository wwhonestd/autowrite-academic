/**
 * Todo List Application
 * A simple, accessible todo list built with vanilla JavaScript
 */

class TodoApp {
    constructor() {
        // Application state
        this.todos = [];
        this.currentFilter = 'all';
        this.nextId = 1;
        
        // DOM elements
        this.elements = {};
        
        // Initialize the application
        this.init();
    }

    /**
     * Initialize the application
     */
    init() {
        try {
            this.bindElements();
            this.attachEventListeners();
            this.loadTodos();
            this.render();
            
            console.log('Todo App initialized successfully');
        } catch (error) {
            this.handleError('Failed to initialize Todo App', error);
        }
    }

    /**
     * Bind DOM elements to the application
     */
    bindElements() {
        const elements = {
            todoForm: '#todo-form',
            todoInput: '#todo-input',
            todoList: '#todo-list',
            todoCount: '#todo-count',
            filterBtns: '[data-filter]',
            clearCompleted: '#clear-completed'
        };

        for (const [key, selector] of Object.entries(elements)) {
            const element = document.querySelector(selector);
            if (!element && key !== 'filterBtns') {
                throw new Error(`Required element not found: ${selector}`);
            }
            this.elements[key] = element;
        }

        // Get all filter buttons
        this.elements.filterBtns = document.querySelectorAll('[data-filter]');
    }

    /**
     * Attach event listeners
     */
    attachEventListeners() {
        // Form submission
        this.elements.todoForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleAddTodo();
        });

        // Filter buttons
        this.elements.filterBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.handleFilterChange(e.target.dataset.filter);
            });
        });

        // Clear completed button
        this.elements.clearCompleted.addEventListener('click', () => {
            this.handleClearCompleted();
        });

        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            this.handleKeyboardShortcuts(e);
        });

        // Handle storage changes from other tabs
        window.addEventListener('storage', (e) => {
            if (e.key === 'todos') {
                this.loadTodos();
                this.render();
            }
        });
    }

    /**
     * Handle adding a new todo
     */
    handleAddTodo() {
        try {
            const text = this.elements.todoInput.value.trim();
            
            if (!text) {
                this.showMessage('Please enter a todo item', 'warning');
                return;
            }

            const todo = {
                id: this.nextId++,
                text: text,
                completed: false,
                createdAt: new Date().toISOString()
            };

            this.todos.unshift(todo);
            this.elements.todoInput.value = '';
            this.saveTodos();
            this.render();
            
            this.showMessage(`Added: "${text}"`, 'success');
        } catch (error) {
            this.handleError('Failed to add todo', error);
        }
    }

    /**
     * Handle filter changes
     */
    handleFilterChange(filter) {
        try {
            this.currentFilter = filter;
            
            // Update active filter button
            this.elements.filterBtns.forEach(btn => {
                btn.classList.toggle('active', btn.dataset.filter === filter);
            });
            
            this.render();
        } catch (error) {
            this.handleError('Failed to change filter', error);
        }
    }

    /**
     * Handle clearing completed todos
     */
    handleClearCompleted() {
        try {
            const completedCount = this.todos.filter(todo => todo.completed).length;
            
            if (completedCount === 0) {
                this.showMessage('No completed items to clear', 'info');
                return;
            }

            this.todos = this.todos.filter(todo => !todo.completed);
            this.saveTodos();
            this.render();
            
            this.showMessage(`Cleared ${completedCount} completed item${completedCount !== 1 ? 's' : ''}`, 'success');
        } catch (error) {
            this.handleError('Failed to clear completed todos', error);
        }
    }

    /**
     * Handle keyboard shortcuts
     */
    handleKeyboardShortcuts(e) {
        try {
            // Focus input with Ctrl+/
            if (e.ctrlKey && e.key === '/') {
                e.preventDefault();
                this.elements.todoInput.focus();
            }
            
            // Clear completed with Ctrl+Shift+C
            if (e.ctrlKey && e.shiftKey && e.key === 'C') {
                e.preventDefault();
                this.handleClearCompleted();
            }
        } catch (error) {
            this.handleError('Keyboard shortcut failed', error);
        }
    }

    /**
     * Get filtered todos based on current filter
     */
    getFilteredTodos() {
        switch (this.currentFilter) {
            case 'active':
                return this.todos.filter(todo => !todo.completed);
            case 'completed':
                return this.todos.filter(todo => todo.completed);
            default:
                return this.todos;
        }
    }

    /**
     * Render the application
     */
    render() {
        try {
            this.renderTodoList();
            this.renderTodoCount();
            this.renderClearButton();
        } catch (error) {
            this.handleError('Failed to render application', error);
        }
    }

    /**
     * Render the todo list
     */
    renderTodoList() {
        const filteredTodos = this.getFilteredTodos();
        
        if (filteredTodos.length === 0) {
            this.elements.todoList.innerHTML = this.getEmptyStateHTML();
            return;
        }

        const todosHTML = filteredTodos
            .map(todo => this.getTodoHTML(todo))
            .join('');
            
        this.elements.todoList.innerHTML = todosHTML;
    }

    /**
     * Get empty state HTML
     */
    getEmptyStateHTML() {
        const messages = {
            all: 'No todos yet. Add one above!',
            active: 'No active todos. Great job!',
            completed: 'No completed todos yet.'
        };

        return `
            <li class="empty-state">
                <div class="empty-message">
                    <span class="empty-icon">📝</span>
                    <p>${messages[this.currentFilter]}</p>
                </div>
            </li>
        `;
    }

    /**
     * Get todo item HTML
     */
    getTodoHTML(todo) {
        return `
            <li class="todo-item ${todo.completed ? 'completed' : ''}" data-id="${todo.id}">
                <div class="todo-content">
                    <label class="todo-label">
                        <input 
                            type="checkbox" 
                            class="todo-checkbox" 
                            ${todo.completed ? 'checked' : ''}
                            aria-label="Mark as ${todo.completed ? 'incomplete' : 'complete'}"
                        >
                        <span class="todo-text">${this.escapeHtml(todo.text)}</span>
                    </label>
                </div>
                <div class="todo-actions">
                    <button class="todo-delete" aria-label="Delete todo: ${this.escapeHtml(todo.text)}">
                        <span aria-hidden="true">×</span>
                    </button>
                </div>
            </li>
        `;
    }

    /**
     * Render todo count
     */
    renderTodoCount() {
        const activeTodos = this.todos.filter(todo => !todo.completed);
        const count = activeTodos.length;
        const itemText = count === 1 ? 'item' : 'items';
        
        this.elements.todoCount.textContent = `${count} ${itemText} left`;
    }

    /**
     * Render clear completed button
     */
    renderClearButton() {
        const completedTodos = this.todos.filter(todo => todo.completed);
        this.elements.clearCompleted.disabled = completedTodos.length === 0;
    }

    /**
     * Save todos to localStorage
     */
    saveTodos() {
        try {
            localStorage.setItem('todos', JSON.stringify(this.todos));
            localStorage.setItem('nextId', this.nextId.toString());
        } catch (error) {
            this.handleError('Failed to save todos', error);
        }
    }

    /**
     * Load todos from localStorage
     */
    loadTodos() {
        try {
            const storedTodos = localStorage.getItem('todos');
            const storedNextId = localStorage.getItem('nextId');
            
            if (storedTodos) {
                this.todos = JSON.parse(storedTodos);
            }
            
            if (storedNextId) {
                this.nextId = parseInt(storedNextId, 10);
            }
        } catch (error) {
            this.handleError('Failed to load todos', error);
            // Reset to empty state on load error
            this.todos = [];
            this.nextId = 1;
        }
    }

    /**
     * Show a message to the user
     */
    showMessage(message, type = 'info') {
        // For now, just log to console
        // In a future version, this could show a toast notification
        console.log(`${type.toUpperCase()}: ${message}`);
    }

    /**
     * Handle errors gracefully
     */
    handleError(context, error) {
        console.error(`${context}:`, error);
        
        // Show user-friendly message
        this.showMessage(`Something went wrong. Please try again.`, 'error');
        
        // In production, you might want to send error reports to a service
        if (typeof window.reportError === 'function') {
            window.reportError(context, error);
        }
    }

    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    try {
        window.todoApp = new TodoApp();
    } catch (error) {
        console.error('Failed to start Todo App:', error);
        
        // Show fallback error message
        document.body.innerHTML = `
            <div style="text-align: center; padding: 2rem; font-family: system-ui, sans-serif;">
                <h1>Todo App Error</h1>
                <p>Sorry, the application failed to start. Please refresh the page to try again.</p>
                <details style="margin-top: 1rem; text-align: left; max-width: 500px; margin-left: auto; margin-right: auto;">
                    <summary>Technical Details</summary>
                    <pre style="background: #f5f5f5; padding: 1rem; border-radius: 4px; overflow: auto;">${error.message}</pre>
                </details>
            </div>
        `;
    }
});

// Development helpers
if (process?.env?.NODE_ENV === 'development') {
    window.todoAppHelpers = {
        clearAllData: () => {
            localStorage.removeItem('todos');
            localStorage.removeItem('nextId');
            location.reload();
        },
        exportData: () => {
            return {
                todos: JSON.parse(localStorage.getItem('todos') || '[]'),
                nextId: localStorage.getItem('nextId')
            };
        }
    };
}