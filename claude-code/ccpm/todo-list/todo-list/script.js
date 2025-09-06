/**
 * Todo List Application
 * A simple, accessible todo list built with vanilla JavaScript
 */

class TodoApp {
    constructor() {
        // Application state
        this.todos = [];
        this.currentFilter = 'all';
        
        // Constants for data validation
        this.STORAGE_KEY = 'todos';
        this.MIN_TEXT_LENGTH = 1;
        this.MAX_TEXT_LENGTH = 500;
        
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
            if (e.key === this.STORAGE_KEY) {
                this.loadTodos();
                this.render();
            }
        });

        // Delegate todo item interactions
        this.elements.todoList.addEventListener('change', (e) => {
            if (e.target.matches('.todo-checkbox')) {
                const todoItem = e.target.closest('.todo-item');
                const todoId = todoItem.dataset.id;
                this.handleToggleTodo(todoId);
            }
        });

        this.elements.todoList.addEventListener('click', (e) => {
            if (e.target.matches('.todo-delete') || e.target.closest('.todo-delete')) {
                const todoItem = e.target.closest('.todo-item');
                const todoId = todoItem.dataset.id;
                this.handleDeleteTodo(todoId);
            } else if (e.target.matches('.todo-edit') || e.target.closest('.todo-edit')) {
                const todoItem = e.target.closest('.todo-item');
                const todoId = todoItem.dataset.id;
                this.handleEditTodo(todoId);
            } else if (e.target.matches('.todo-text') && !e.target.closest('.todo-item').classList.contains('editing')) {
                const todoItem = e.target.closest('.todo-item');
                const todoId = todoItem.dataset.id;
                this.handleEditTodo(todoId);
            }
        });

        // Handle keyboard events for edit mode
        this.elements.todoList.addEventListener('keydown', (e) => {
            if (e.target.matches('.todo-edit-input')) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.handleSaveEdit(e.target);
                } else if (e.key === 'Escape') {
                    e.preventDefault();
                    this.handleCancelEdit(e.target);
                }
            }
        });

        // Handle blur for edit mode
        this.elements.todoList.addEventListener('blur', (e) => {
            if (e.target.matches('.todo-edit-input')) {
                // Small delay to allow click events to fire first
                setTimeout(() => {
                    this.handleSaveEdit(e.target);
                }, 100);
            }
        }, true);
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

            // Validate text length
            if (text.length > this.MAX_TEXT_LENGTH) {
                this.showMessage(`Todo text cannot exceed ${this.MAX_TEXT_LENGTH} characters`, 'warning');
                return;
            }

            const todo = {
                id: this.generateId(),
                text: text,
                completed: false,
                created: new Date().toISOString()
            };

            // Validate the todo before adding
            this.validateTodo(todo);

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
     * Handle toggling a todo's completion status
     */
    handleToggleTodo(todoId) {
        try {
            const todoIndex = this.todos.findIndex(todo => todo.id === todoId);
            
            if (todoIndex === -1) {
                throw new Error(`Todo not found: ${todoId}`);
            }

            const todo = this.todos[todoIndex];
            const wasCompleted = todo.completed;
            
            // Toggle completion status
            todo.completed = !todo.completed;
            
            this.saveTodos();
            this.render();
            
            const status = todo.completed ? 'completed' : 'uncompleted';
            this.showMessage(`Todo "${todo.text}" marked as ${status}`, 'success');
        } catch (error) {
            this.handleError('Failed to toggle todo', error);
        }
    }

    /**
     * Handle deleting a todo
     */
    handleDeleteTodo(todoId) {
        try {
            const todoIndex = this.todos.findIndex(todo => todo.id === todoId);
            
            if (todoIndex === -1) {
                throw new Error(`Todo not found: ${todoId}`);
            }

            const todo = this.todos[todoIndex];
            const todoText = todo.text;
            
            // Show confirmation dialog
            if (!this.showConfirmDialog(`Delete "${todoText}"?`, 'This action cannot be undone.')) {
                return;
            }
            
            // Remove todo from array
            this.todos.splice(todoIndex, 1);
            
            this.saveTodos();
            this.render();
            
            this.showMessage(`Deleted: "${todoText}"`, 'success');
        } catch (error) {
            this.handleError('Failed to delete todo', error);
        }
    }

    /**
     * Handle editing a todo
     */
    handleEditTodo(todoId) {
        try {
            const todoItem = document.querySelector(`[data-id="${todoId}"]`);
            if (!todoItem) {
                throw new Error(`Todo item not found in DOM: ${todoId}`);
            }

            // Check if already editing
            if (todoItem.classList.contains('editing')) {
                return;
            }

            const todo = this.todos.find(t => t.id === todoId);
            if (!todo) {
                throw new Error(`Todo not found: ${todoId}`);
            }

            // Add editing class
            todoItem.classList.add('editing');

            // Find the text element and replace with input
            const textElement = todoItem.querySelector('.todo-text');
            if (!textElement) {
                throw new Error('Todo text element not found');
            }

            const currentText = todo.text;
            textElement.innerHTML = `<input type="text" class="todo-edit-input" value="${this.escapeHtml(currentText)}" data-original-text="${this.escapeHtml(currentText)}" maxlength="${this.MAX_TEXT_LENGTH}">`;

            // Focus the input and select all text
            const input = textElement.querySelector('.todo-edit-input');
            input.focus();
            input.select();

        } catch (error) {
            this.handleError('Failed to start editing todo', error);
        }
    }

    /**
     * Handle saving an edit
     */
    handleSaveEdit(input) {
        try {
            if (!input || !input.classList.contains('todo-edit-input')) {
                return;
            }

            const todoItem = input.closest('.todo-item');
            if (!todoItem) {
                throw new Error('Todo item not found');
            }

            const todoId = todoItem.dataset.id;
            const newText = input.value.trim();
            const originalText = input.dataset.originalText || '';

            // If text hasn't changed, just cancel
            if (newText === originalText) {
                this.handleCancelEdit(input);
                return;
            }

            // Validate new text
            if (!newText) {
                this.showMessage('Todo text cannot be empty', 'warning');
                input.focus();
                return;
            }

            if (newText.length > this.MAX_TEXT_LENGTH) {
                this.showMessage(`Todo text cannot exceed ${this.MAX_TEXT_LENGTH} characters`, 'warning');
                input.focus();
                return;
            }

            // Update the todo
            this.updateTodo(todoId, { text: newText });
            
            // Remove editing state
            todoItem.classList.remove('editing');
            
            // Re-render to show updated text
            this.render();
            
            this.showMessage(`Updated: "${newText}"`, 'success');

        } catch (error) {
            this.handleError('Failed to save todo edit', error);
            this.handleCancelEdit(input);
        }
    }

    /**
     * Handle canceling an edit
     */
    handleCancelEdit(input) {
        try {
            if (!input || !input.classList.contains('todo-edit-input')) {
                return;
            }

            const todoItem = input.closest('.todo-item');
            if (!todoItem) {
                return;
            }

            // Remove editing state
            todoItem.classList.remove('editing');
            
            // Re-render to restore original text
            this.render();

        } catch (error) {
            this.handleError('Failed to cancel todo edit', error);
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

    // ===== CRUD OPERATIONS =====

    /**
     * Create a new todo and add it to storage
     */
    addTodo(text) {
        if (typeof text !== 'string' || !text.trim()) {
            throw new Error('Todo text must be a non-empty string');
        }

        const trimmedText = text.trim();
        if (trimmedText.length > this.MAX_TEXT_LENGTH) {
            throw new Error(`Todo text cannot exceed ${this.MAX_TEXT_LENGTH} characters`);
        }

        const todo = {
            id: this.generateId(),
            text: trimmedText,
            completed: false,
            created: new Date().toISOString()
        };

        this.validateTodo(todo);
        this.todos.unshift(todo);
        this.saveTodos();

        return todo;
    }

    /**
     * Update an existing todo
     */
    updateTodo(todoId, updates) {
        if (!todoId) {
            throw new Error('Todo ID is required');
        }

        if (!updates || typeof updates !== 'object') {
            throw new Error('Updates must be an object');
        }

        const todoIndex = this.todos.findIndex(todo => todo.id === todoId);
        if (todoIndex === -1) {
            throw new Error(`Todo not found: ${todoId}`);
        }

        const todo = { ...this.todos[todoIndex] };

        // Apply updates
        if ('text' in updates) {
            if (typeof updates.text !== 'string') {
                throw new Error('Todo text must be a string');
            }
            const trimmedText = updates.text.trim();
            if (trimmedText.length === 0) {
                throw new Error('Todo text cannot be empty');
            }
            if (trimmedText.length > this.MAX_TEXT_LENGTH) {
                throw new Error(`Todo text cannot exceed ${this.MAX_TEXT_LENGTH} characters`);
            }
            todo.text = trimmedText;
        }

        if ('completed' in updates) {
            if (typeof updates.completed !== 'boolean') {
                throw new Error('Todo completed must be a boolean');
            }
            todo.completed = updates.completed;
        }

        // Validate updated todo
        this.validateTodo(todo);

        // Update in array
        this.todos[todoIndex] = todo;
        this.saveTodos();

        return todo;
    }

    /**
     * Delete a todo
     */
    deleteTodo(todoId) {
        if (!todoId) {
            throw new Error('Todo ID is required');
        }

        const todoIndex = this.todos.findIndex(todo => todo.id === todoId);
        if (todoIndex === -1) {
            throw new Error(`Todo not found: ${todoId}`);
        }

        const todo = this.todos[todoIndex];
        this.todos.splice(todoIndex, 1);
        this.saveTodos();

        return todo;
    }

    /**
     * Toggle a todo's completion status
     */
    toggleTodo(todoId) {
        if (!todoId) {
            throw new Error('Todo ID is required');
        }

        const todoIndex = this.todos.findIndex(todo => todo.id === todoId);
        if (todoIndex === -1) {
            throw new Error(`Todo not found: ${todoId}`);
        }

        const todo = this.todos[todoIndex];
        todo.completed = !todo.completed;
        this.saveTodos();

        return todo;
    }

    /**
     * Get all todos (read operation)
     */
    getTodos() {
        // Return a deep copy to prevent external modification
        return JSON.parse(JSON.stringify(this.todos));
    }

    /**
     * Get a todo by ID
     */
    getTodo(todoId) {
        if (!todoId) {
            throw new Error('Todo ID is required');
        }

        const todo = this.todos.find(todo => todo.id === todoId);
        if (!todo) {
            throw new Error(`Todo not found: ${todoId}`);
        }

        // Return a deep copy to prevent external modification
        return JSON.parse(JSON.stringify(todo));
    }

    /**
     * Clear all todos (primarily for testing/reset purposes)
     */
    clearAllTodos() {
        this.todos = [];
        this.saveTodos();
        return true;
    }

    // ===== UI METHODS =====

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
        const stateConfig = {
            all: {
                icon: '📝',
                title: 'Your todo list is empty',
                message: 'Add your first task to get started with staying organized!'
            },
            active: {
                icon: '🎉',
                title: 'All done!',
                message: 'You have no active tasks. Time to celebrate or add something new!'
            },
            completed: {
                icon: '✨',
                title: 'No completed tasks yet',
                message: 'Complete some tasks to see them here. You got this!'
            }
        };

        const state = stateConfig[this.currentFilter];
        
        return `
            <li class="empty-state">
                <div class="empty-message">
                    <span class="empty-icon">${state.icon}</span>
                    <h3>${state.title}</h3>
                    <p>${state.message}</p>
                </div>
            </li>
        `;
    }

    /**
     * Get todo item HTML
     */
    getTodoHTML(todo) {
        const createdDate = new Date(todo.created);
        const timeAgo = this.getTimeAgo(createdDate);
        
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
                        <span class="todo-text" title="Click to edit">${this.escapeHtml(todo.text)}</span>
                    </label>
                    <div class="todo-meta">
                        <span class="todo-timestamp" title="Created ${createdDate.toLocaleString()}">${timeAgo}</span>
                    </div>
                </div>
                <div class="todo-actions">
                    <button class="todo-edit" aria-label="Edit todo: ${this.escapeHtml(todo.text)}" title="Edit">
                        <span aria-hidden="true">✏️</span>
                    </button>
                    <button class="todo-delete" aria-label="Delete todo: ${this.escapeHtml(todo.text)}" title="Delete">
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
     * Generate unique timestamp-based ID
     */
    generateId() {
        return `todo_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    /**
     * Validate todo data structure
     */
    validateTodo(todo) {
        if (!todo || typeof todo !== 'object') {
            throw new Error('Todo must be an object');
        }

        if (typeof todo.id !== 'string' || !todo.id.trim()) {
            throw new Error('Todo must have a valid string ID');
        }

        if (typeof todo.text !== 'string') {
            throw new Error('Todo text must be a string');
        }

        const text = todo.text.trim();
        if (text.length < this.MIN_TEXT_LENGTH) {
            throw new Error('Todo text cannot be empty');
        }

        if (text.length > this.MAX_TEXT_LENGTH) {
            throw new Error(`Todo text cannot exceed ${this.MAX_TEXT_LENGTH} characters`);
        }

        if (typeof todo.completed !== 'boolean') {
            throw new Error('Todo completed must be a boolean');
        }

        if (typeof todo.created !== 'string' || !this.isValidISOString(todo.created)) {
            throw new Error('Todo must have a valid ISO timestamp for created field');
        }

        return true;
    }

    /**
     * Validate ISO timestamp string
     */
    isValidISOString(dateString) {
        try {
            const date = new Date(dateString);
            return date instanceof Date && !isNaN(date) && dateString === date.toISOString();
        } catch {
            return false;
        }
    }

    /**
     * Check localStorage availability and quota
     */
    checkLocalStorageAvailability() {
        try {
            if (typeof Storage === 'undefined' || !window.localStorage) {
                throw new Error('localStorage is not available');
            }

            // Test localStorage with a small value
            const testKey = '__ls_test__';
            localStorage.setItem(testKey, 'test');
            localStorage.removeItem(testKey);
            
            return true;
        } catch (error) {
            throw new Error(`localStorage not available: ${error.message}`);
        }
    }

    /**
     * Estimate storage size needed for todos
     */
    estimateStorageSize(todos) {
        try {
            return JSON.stringify(todos).length;
        } catch (error) {
            throw new Error('Cannot estimate storage size: data not serializable');
        }
    }

    /**
     * Save todos to localStorage with enhanced error handling
     */
    saveTodos() {
        try {
            // Check localStorage availability
            this.checkLocalStorageAvailability();

            // Validate all todos before saving
            this.todos.forEach((todo, index) => {
                try {
                    this.validateTodo(todo);
                } catch (error) {
                    throw new Error(`Invalid todo at index ${index}: ${error.message}`);
                }
            });

            // Estimate storage size
            const dataSize = this.estimateStorageSize(this.todos);
            
            // Check if we're approaching quota (most browsers allow ~5-10MB)
            if (dataSize > 4 * 1024 * 1024) { // 4MB warning threshold
                console.warn(`Large data size detected: ${Math.round(dataSize / 1024)}KB`);
            }

            // Save to localStorage
            localStorage.setItem(this.STORAGE_KEY, JSON.stringify(this.todos));
            
            console.log(`Saved ${this.todos.length} todos (${Math.round(dataSize / 1024)}KB)`);
        } catch (error) {
            // Handle quota exceeded error specifically
            if (error.name === 'QuotaExceededError' || error.code === 22) {
                this.handleStorageQuotaExceeded();
            } else {
                this.handleError('Failed to save todos to localStorage', error);
            }
        }
    }

    /**
     * Handle localStorage quota exceeded
     */
    handleStorageQuotaExceeded() {
        console.warn('localStorage quota exceeded');
        
        // Try to free up space by removing old completed todos
        const originalCount = this.todos.length;
        const cutoffDate = new Date();
        cutoffDate.setDate(cutoffDate.getDate() - 30); // Remove completed todos older than 30 days
        
        this.todos = this.todos.filter(todo => {
            if (!todo.completed) return true;
            if (!todo.created) return true; // Keep todos without created date to be safe
            
            try {
                const todoDate = new Date(todo.created);
                return todoDate > cutoffDate;
            } catch {
                return true; // Keep todos with invalid dates to be safe
            }
        });
        
        const removedCount = originalCount - this.todos.length;
        
        if (removedCount > 0) {
            console.log(`Removed ${removedCount} old completed todos to free space`);
            this.showMessage(`Removed ${removedCount} old completed items to free storage space`, 'info');
            
            // Try saving again
            try {
                localStorage.setItem(this.STORAGE_KEY, JSON.stringify(this.todos));
            } catch (error) {
                this.showMessage('Storage still full. Please clear more items manually.', 'warning');
            }
        } else {
            this.showMessage('Storage quota exceeded. Please clear some completed items.', 'warning');
        }
    }

    /**
     * Load todos from localStorage with enhanced error handling
     */
    loadTodos() {
        try {
            // Check localStorage availability
            this.checkLocalStorageAvailability();
            
            const storedTodos = localStorage.getItem(this.STORAGE_KEY);
            
            if (!storedTodos) {
                console.log('No stored todos found, starting fresh');
                this.todos = [];
                return;
            }

            // Parse stored data
            let parsedTodos;
            try {
                parsedTodos = JSON.parse(storedTodos);
            } catch (parseError) {
                throw new Error(`Corrupted todo data: ${parseError.message}`);
            }

            // Validate data structure
            if (!Array.isArray(parsedTodos)) {
                throw new Error('Stored todos is not an array');
            }

            // Validate and clean up individual todos
            const validTodos = [];
            const invalidTodos = [];

            parsedTodos.forEach((todo, index) => {
                try {
                    // Try to fix common issues before validation
                    if (todo && typeof todo === 'object') {
                        // Convert old numeric IDs to string format
                        if (typeof todo.id === 'number') {
                            todo.id = `todo_${todo.id}_${Date.now()}`;
                        }
                        
                        // Add missing created timestamp
                        if (!todo.created && todo.createdAt) {
                            todo.created = todo.createdAt;
                        } else if (!todo.created) {
                            todo.created = new Date().toISOString();
                        }
                        
                        // Ensure boolean completed field
                        if (typeof todo.completed !== 'boolean') {
                            todo.completed = Boolean(todo.completed);
                        }

                        // Trim and validate text
                        if (typeof todo.text === 'string') {
                            todo.text = todo.text.trim();
                        }
                    }

                    this.validateTodo(todo);
                    validTodos.push(todo);
                } catch (validationError) {
                    console.warn(`Invalid todo at index ${index}:`, validationError.message, todo);
                    invalidTodos.push({ index, todo, error: validationError.message });
                }
            });

            this.todos = validTodos;

            if (invalidTodos.length > 0) {
                console.warn(`Loaded ${validTodos.length} valid todos, skipped ${invalidTodos.length} invalid ones`);
                this.showMessage(`Recovered ${validTodos.length} todos, ${invalidTodos.length} corrupted items were removed`, 'warning');
                
                // Save cleaned data back to localStorage
                this.saveTodos();
            } else {
                console.log(`Loaded ${validTodos.length} todos successfully`);
            }

        } catch (error) {
            this.handleError('Failed to load todos from localStorage', error);
            
            // Try to backup corrupted data before resetting
            try {
                const corruptedData = localStorage.getItem(this.STORAGE_KEY);
                if (corruptedData) {
                    localStorage.setItem(`${this.STORAGE_KEY}_backup_${Date.now()}`, corruptedData);
                    console.log('Corrupted data backed up before reset');
                }
            } catch (backupError) {
                console.warn('Could not backup corrupted data:', backupError);
            }
            
            // Reset to empty state on load error
            this.todos = [];
            this.showMessage('Todo data was corrupted and has been reset. Starting fresh.', 'warning');
        }
    }

    /**
     * Show a confirmation dialog
     */
    showConfirmDialog(title, message) {
        return confirm(`${title}\n\n${message}`);
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
     * Get relative time string (e.g., "2 minutes ago")
     */
    getTimeAgo(date) {
        const now = new Date();
        const diffInSeconds = Math.floor((now - date) / 1000);

        if (diffInSeconds < 60) {
            return diffInSeconds < 5 ? 'just now' : `${diffInSeconds}s ago`;
        }

        const diffInMinutes = Math.floor(diffInSeconds / 60);
        if (diffInMinutes < 60) {
            return `${diffInMinutes}m ago`;
        }

        const diffInHours = Math.floor(diffInMinutes / 60);
        if (diffInHours < 24) {
            return `${diffInHours}h ago`;
        }

        const diffInDays = Math.floor(diffInHours / 24);
        if (diffInDays < 7) {
            return `${diffInDays}d ago`;
        }

        const diffInWeeks = Math.floor(diffInDays / 7);
        if (diffInWeeks < 4) {
            return `${diffInWeeks}w ago`;
        }

        // For older items, show the date
        return date.toLocaleDateString();
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
if (typeof process === 'undefined' || process?.env?.NODE_ENV === 'development') {
    window.todoAppHelpers = {
        clearAllData: () => {
            localStorage.removeItem('todos');
            // Clean up old format data
            localStorage.removeItem('nextId');
            location.reload();
        },
        exportData: () => {
            return {
                todos: JSON.parse(localStorage.getItem('todos') || '[]'),
                backupKeys: Object.keys(localStorage).filter(key => key.startsWith('todos_backup_'))
            };
        },
        importData: (data) => {
            if (data && Array.isArray(data.todos)) {
                localStorage.setItem('todos', JSON.stringify(data.todos));
                location.reload();
            }
        },
        validateStorage: () => {
            try {
                const app = window.todoApp;
                if (!app) return 'TodoApp not initialized';
                
                app.checkLocalStorageAvailability();
                const todos = app.getTodos();
                todos.forEach(app.validateTodo.bind(app));
                
                return `✅ Storage valid: ${todos.length} todos`;
            } catch (error) {
                return `❌ Storage invalid: ${error.message}`;
            }
        }
    };
}