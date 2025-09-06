/**
 * Optimized Todo List Application
 * Performance-focused version with DOM optimization and caching
 */

class TodoApp {
    constructor() {
        // Application state
        this.todos = [];
        this.currentFilter = 'all';
        
        // Performance optimizations
        this.domCache = new Map();
        this.renderScheduled = false;
        this.filteredTodosCache = null;
        this.filterCacheKey = '';
        
        // Constants
        this.STORAGE_KEY = 'todos';
        this.MIN_TEXT_LENGTH = 1;
        this.MAX_TEXT_LENGTH = 500;
        this.DEBOUNCE_DELAY = 16; // ~60fps
        
        // DOM elements - cached for performance
        this.elements = {};
        
        this.init();
    }

    init() {
        try {
            this.bindElements();
            this.attachEventListeners();
            this.loadTodos();
            this.scheduleRender();
            
            console.log('Todo App initialized successfully');
        } catch (error) {
            this.handleError('Failed to initialize Todo App', error);
        }
    }

    // Optimized DOM element binding with caching
    bindElements() {
        const selectors = {
            todoForm: '#todo-form',
            todoInput: '#todo-input',
            todoList: '#todo-list',
            todoCount: '#todo-count',
            filterBtns: '[data-filter]',
            clearCompleted: '#clear-completed'
        };

        Object.entries(selectors).forEach(([key, selector]) => {
            if (key === 'filterBtns') {
                this.elements[key] = Array.from(document.querySelectorAll(selector));
            } else {
                const element = document.querySelector(selector);
                if (!element) {
                    throw new Error(`Required element not found: ${selector}`);
                }
                this.elements[key] = element;
            }
        });
    }

    // Optimized event listeners with event delegation
    attachEventListeners() {
        // Form submission with debouncing
        this.elements.todoForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const text = this.elements.todoInput.value.trim();
            if (text) {
                this.addTodo(text);
            }
        });

        // Filter buttons with event delegation
        this.elements.filterBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                this.setFilter(btn.dataset.filter);
            });
        });

        // Clear completed
        this.elements.clearCompleted.addEventListener('click', (e) => {
            e.preventDefault();
            this.handleClearCompleted();
        });

        // Cross-tab synchronization
        window.addEventListener('storage', (e) => {
            if (e.key === this.STORAGE_KEY) {
                this.loadTodos();
                this.invalidateCache();
                this.scheduleRender();
            }
        });

        // Efficient event delegation for todo items
        this.elements.todoList.addEventListener('click', (e) => {
            const todoItem = e.target.closest('.todo-item');
            if (!todoItem) return;

            const todoId = todoItem.dataset.id;

            if (e.target.matches('.todo-checkbox')) {
                this.toggleTodo(todoId);
            } else if (e.target.matches('.edit-btn')) {
                e.preventDefault();
                this.handleEditTodo(todoId);
            } else if (e.target.matches('.delete-btn')) {
                e.preventDefault();
                this.handleDeleteTodo(todoId);
            }
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', this.handleKeyboardShortcuts.bind(this));
    }

    // Performance-optimized todo addition
    addTodo(text) {
        try {
            const trimmedText = text.trim();
            if (trimmedText.length < this.MIN_TEXT_LENGTH || trimmedText.length > this.MAX_TEXT_LENGTH) {
                throw new Error(`Text must be between ${this.MIN_TEXT_LENGTH} and ${this.MAX_TEXT_LENGTH} characters`);
            }

            const todo = {
                id: this.generateId(),
                text: trimmedText,
                completed: false,
                created: Date.now() // Use timestamp for better performance
            };

            this.todos.unshift(todo);
            this.elements.todoInput.value = '';
            this.saveTodos();
            this.invalidateCache();
            this.scheduleRender();
            
            this.showMessage(`Added: "${trimmedText}"`, 'success');
        } catch (error) {
            this.handleError('Failed to add todo', error);
        }
    }

    // Optimized toggle with minimal DOM updates
    toggleTodo(todoId) {
        try {
            const todo = this.todos.find(t => t.id === todoId);
            if (!todo) {
                throw new Error(`Todo not found: ${todoId}`);
            }

            todo.completed = !todo.completed;
            this.saveTodos();
            
            // Update only the specific item instead of full render
            this.updateTodoItem(todoId, todo);
            this.invalidateCache();
            this.updateCount();
            this.updateClearButton();
            
            const status = todo.completed ? 'completed' : 'uncompleted';
            this.showMessage(`Todo marked as ${status}`, 'success');
        } catch (error) {
            this.handleError('Failed to toggle todo', error);
        }
    }

    // Fast update of individual todo item
    updateTodoItem(todoId, todo) {
        const todoElement = document.querySelector(`[data-id="${todoId}"]`);
        if (!todoElement) return;

        const checkbox = todoElement.querySelector('.todo-checkbox');
        const label = todoElement.querySelector('.todo-text');
        
        if (checkbox) checkbox.checked = todo.completed;
        if (label) label.textContent = todo.text;
        
        todoElement.classList.toggle('completed', todo.completed);
    }

    // Optimized delete with confirmation
    deleteTodo(todoId) {
        try {
            const todoIndex = this.todos.findIndex(t => t.id === todoId);
            if (todoIndex === -1) {
                throw new Error(`Todo not found: ${todoId}`);
            }

            const todo = this.todos[todoIndex];
            this.todos.splice(todoIndex, 1);
            this.saveTodos();
            this.invalidateCache();
            this.scheduleRender();
            
            this.showMessage(`Deleted: "${todo.text}"`, 'success');
        } catch (error) {
            this.handleError('Failed to delete todo', error);
        }
    }

    handleDeleteTodo(todoId) {
        const todo = this.todos.find(t => t.id === todoId);
        if (!todo) return;

        if (confirm(`Delete "${todo.text}"?\n\nThis action cannot be undone.`)) {
            this.deleteTodo(todoId);
        }
    }

    // Cache-aware filter setting
    setFilter(filter) {
        if (this.currentFilter === filter) return;
        
        this.currentFilter = filter;
        this.updateFilterButtons();
        this.invalidateCache();
        this.scheduleRender();
    }

    // Fast filter button update
    updateFilterButtons() {
        this.elements.filterBtns.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.filter === this.currentFilter);
        });
    }

    // Clear completed with batch operation
    handleClearCompleted() {
        try {
            const initialCount = this.todos.length;
            this.todos = this.todos.filter(todo => !todo.completed);
            const clearedCount = initialCount - this.todos.length;
            
            if (clearedCount === 0) {
                this.showMessage('No completed items to clear', 'info');
                return;
            }

            this.saveTodos();
            this.invalidateCache();
            this.scheduleRender();
            
            this.showMessage(`Cleared ${clearedCount} item${clearedCount !== 1 ? 's' : ''}`, 'success');
        } catch (error) {
            this.handleError('Failed to clear completed todos', error);
        }
    }

    // Cached filtered todos with performance optimization
    getFilteredTodos() {
        const cacheKey = `${this.currentFilter}_${this.todos.length}_${this.todos.filter(t => t.completed).length}`;
        
        if (this.filteredTodosCache && this.filterCacheKey === cacheKey) {
            return this.filteredTodosCache;
        }

        let filtered;
        switch (this.currentFilter) {
            case 'active':
                filtered = this.todos.filter(todo => !todo.completed);
                break;
            case 'completed':
                filtered = this.todos.filter(todo => todo.completed);
                break;
            default:
                filtered = this.todos;
        }

        this.filteredTodosCache = filtered;
        this.filterCacheKey = cacheKey;
        return filtered;
    }

    // Cache invalidation
    invalidateCache() {
        this.filteredTodosCache = null;
        this.filterCacheKey = '';
        this.domCache.clear();
    }

    // Debounced render scheduling for performance
    scheduleRender() {
        if (this.renderScheduled) return;
        
        this.renderScheduled = true;
        requestAnimationFrame(() => {
            this.render();
            this.renderScheduled = false;
        });
    }

    // Main render function with optimizations
    render() {
        try {
            this.renderTodoList();
            this.updateCount();
            this.updateClearButton();
        } catch (error) {
            this.handleError('Failed to render application', error);
        }
    }

    // Optimized todo list rendering with DOM reuse
    renderTodoList() {
        const filteredTodos = this.getFilteredTodos();
        const todoList = this.elements.todoList;
        
        if (filteredTodos.length === 0) {
            todoList.innerHTML = this.getEmptyStateHTML();
            return;
        }

        // Use document fragment for better performance
        const fragment = document.createDocumentFragment();
        
        filteredTodos.forEach(todo => {
            const todoElement = this.createTodoElement(todo);
            fragment.appendChild(todoElement);
        });

        // Single DOM update
        todoList.innerHTML = '';
        todoList.appendChild(fragment);
    }

    // Optimized todo element creation
    createTodoElement(todo) {
        const li = document.createElement('li');
        li.className = `todo-item${todo.completed ? ' completed' : ''}`;
        li.dataset.id = todo.id;

        // Using template literal for better performance than string concatenation
        li.innerHTML = `
            <div class="todo-content">
                <input type="checkbox" class="todo-checkbox" ${todo.completed ? 'checked' : ''} 
                       id="todo-${todo.id}" aria-describedby="todo-text-${todo.id}">
                <label for="todo-${todo.id}" class="todo-text" id="todo-text-${todo.id}">
                    ${this.escapeHtml(todo.text)}
                </label>
            </div>
            <div class="todo-actions">
                <button class="action-btn edit-btn" aria-label="Edit todo">Edit</button>
                <button class="action-btn delete-btn" aria-label="Delete todo">Delete</button>
            </div>
        `;

        return li;
    }

    // Fast count update without re-rendering
    updateCount() {
        const activeCount = this.todos.reduce((count, todo) => count + (!todo.completed ? 1 : 0), 0);
        this.elements.todoCount.textContent = `${activeCount} ${activeCount === 1 ? 'item' : 'items'} left`;
    }

    // Fast clear button update
    updateClearButton() {
        const hasCompleted = this.todos.some(todo => todo.completed);
        this.elements.clearCompleted.disabled = !hasCompleted;
    }

    // Get empty state HTML with caching
    getEmptyStateHTML() {
        const cacheKey = `empty_${this.currentFilter}`;
        if (this.domCache.has(cacheKey)) {
            return this.domCache.get(cacheKey);
        }

        const states = {
            all: { icon: '📝', title: 'Your todo list is empty', 
                   message: 'Add your first task to get started!' },
            active: { icon: '🎉', title: 'All done!', 
                      message: 'You have no active tasks!' },
            completed: { icon: '📋', title: 'No completed tasks', 
                         message: 'Completed tasks will appear here.' }
        };

        const state = states[this.currentFilter] || states.all;
        const html = `
            <li class="empty-state">
                <div class="empty-icon">${state.icon}</div>
                <h3 class="empty-title">${state.title}</h3>
                <p class="empty-message">${state.message}</p>
            </li>
        `;

        this.domCache.set(cacheKey, html);
        return html;
    }

    // Optimized storage operations
    saveTodos() {
        try {
            // Use JSON.stringify with minimal data
            const data = this.todos.map(todo => ({
                id: todo.id,
                text: todo.text,
                completed: todo.completed,
                created: todo.created
            }));
            
            localStorage.setItem(this.STORAGE_KEY, JSON.stringify(data));
        } catch (error) {
            this.handleError('Failed to save todos', error);
        }
    }

    loadTodos() {
        try {
            const data = localStorage.getItem(this.STORAGE_KEY);
            this.todos = data ? JSON.parse(data) : [];
            this.invalidateCache();
        } catch (error) {
            this.handleError('Failed to load todos', error);
            this.todos = [];
        }
    }

    // Utility methods
    generateId() {
        // More efficient ID generation
        return `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Simplified message system
    showMessage(message, type = 'info') {
        console.log(`${type.toUpperCase()}: ${message}`);
        
        // Simple toast notification
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'error' ? '#dc3545' : type === 'success' ? '#28a745' : '#17a2b8'};
            color: white;
            padding: 12px 20px;
            border-radius: 4px;
            z-index: 1000;
            opacity: 0.9;
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    handleError(message, error) {
        console.error(message, error);
        this.showMessage(message, 'error');
    }

    // Keyboard shortcuts
    handleKeyboardShortcuts(e) {
        // Ctrl/Cmd + A - Show all todos
        if ((e.ctrlKey || e.metaKey) && e.key === 'a' && e.target === document.body) {
            e.preventDefault();
            this.setFilter('all');
        }
        
        // Escape - Clear input
        if (e.key === 'Escape' && e.target === this.elements.todoInput) {
            e.target.value = '';
        }
    }

    // Public API methods for testing
    clearAllTodos() {
        this.todos = [];
        this.saveTodos();
        this.invalidateCache();
        this.scheduleRender();
    }

    getTodos() {
        return [...this.todos];
    }
}

// Initialize app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.todoApp = new TodoApp();
    });
} else {
    window.todoApp = new TodoApp();
}