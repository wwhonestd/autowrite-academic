# Todo List Application

A simple, accessible, and responsive personal todo list application built with vanilla HTML, CSS, and JavaScript.

## Features

- ✅ Add new todos with Enter key or click
- ✅ Mark todos as complete/incomplete
- ✅ Filter todos by status (All, Active, Completed)
- ✅ Delete individual todos
- ✅ Clear all completed todos at once
- ✅ Persistent storage using localStorage
- ✅ Responsive design (mobile-first)
- ✅ Accessible with proper ARIA labels and keyboard navigation
- ✅ Clean, modern UI with CSS custom properties

## Getting Started

### Prerequisites

- A modern web browser (Chrome, Firefox, Safari, Edge)
- No additional dependencies or build tools required

### Installation

1. Clone or download the project files
2. Open `index.html` in your web browser
3. Start managing your todos!

### File Structure

```
todo-list/
├── index.html          # Main HTML structure
├── styles.css          # CSS styles and responsive design
├── script.js           # JavaScript application logic
└── README.md          # This file
```

## Usage

### Basic Operations

- **Add a todo**: Type your task in the input field and press Enter or click the "+" button
- **Complete a todo**: Click the checkbox next to any todo item
- **Delete a todo**: Click the "×" button next to any todo item
- **Filter todos**: Click "All", "Active", or "Completed" to filter the list
- **Clear completed**: Click "Clear Completed" to remove all completed todos

### Keyboard Shortcuts

- `Ctrl + /` - Focus the input field
- `Ctrl + Shift + C` - Clear all completed todos
- `Enter` - Submit new todo when input is focused

### Data Persistence

Your todos are automatically saved to your browser's localStorage and will persist between sessions. Data is synced across browser tabs in real-time.

## Technical Details

### Architecture

The application uses a class-based architecture with the `TodoApp` class managing:

- Application state (todos array, filters, etc.)
- DOM manipulation and rendering
- Event handling and user interactions
- Data persistence with localStorage
- Error handling and user feedback

### Browser Support

- Chrome 60+
- Firefox 60+
- Safari 12+
- Edge 79+

### Accessibility Features

- Semantic HTML structure
- Proper ARIA labels and roles
- Keyboard navigation support
- Screen reader friendly
- High contrast colors
- Focus management

### Performance Features

- Vanilla JavaScript (no external dependencies)
- Efficient DOM updates
- CSS-only animations and transitions
- Mobile-optimized with responsive design
- Minimal bundle size (~15KB total)

## Development

### Code Structure

- **HTML**: Semantic structure with accessibility in mind
- **CSS**: Mobile-first responsive design using CSS Grid/Flexbox
- **JavaScript**: ES6+ class-based architecture with error handling

### Styling System

The CSS uses a design token system with CSS custom properties for:

- Colors (semantic color palette)
- Typography (font sizes, weights, line heights)
- Spacing (consistent spacing scale)
- Border radius and shadows
- Transitions and animations

### Error Handling

The application includes comprehensive error handling:

- Graceful degradation for missing DOM elements
- localStorage access error handling
- User-friendly error messages
- Development helpers for debugging

## Browser Testing

The application has been tested in:

- ✅ Chrome (latest)
- ✅ Firefox (latest)
- ✅ Safari (latest)
- ✅ Edge (latest)
- ✅ Mobile browsers (iOS Safari, Android Chrome)

## Future Enhancements

Potential features for future versions:

- [ ] Todo editing (double-click to edit)
- [ ] Due dates and reminders
- [ ] Categories and tags
- [ ] Drag and drop reordering
- [ ] Import/export functionality
- [ ] Dark mode toggle
- [ ] Progressive Web App (PWA) support
- [ ] Cloud synchronization

## Contributing

This is a personal project, but suggestions and improvements are welcome! Please ensure any changes maintain:

- Accessibility standards
- Cross-browser compatibility
- Clean, readable code
- Responsive design principles

## License

This project is open source and available under the [MIT License](LICENSE).

## Changelog

### Version 1.0.0 (Current)
- Initial release with core todo functionality
- Responsive design and accessibility features
- localStorage persistence
- Filter and bulk operations

---

**Built with ❤️ using vanilla JavaScript, HTML, and CSS**