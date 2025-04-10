# Phase 1: Core MVP Implementation Work Plan

## Overview
This plan outlines the tasks required to implement the core MVP functionality for the Second Brain application, focusing on basic journaling and viewing capabilities. The goal is to create a locally runnable application that can create, view, and edit daily Markdown notes with full filesystem integration.

## 1. Project Setup and Infrastructure

### 1.1 Development Environment Setup
- [ ] Create project repository with appropriate structure
- [ ] Set up Go modules and initial dependencies
- [ ] Configure development tools (linters, formatters, etc.)
- [ ] Create initial documentation and README

### 1.2 Docker Configuration
- [ ] Create Dockerfile for Go backend
- [ ] Create Dockerfile for Svelte frontend (dev environment)
- [ ] Create docker-compose.yml for local development
- [ ] Set up volume mappings for journal files and database
- [ ] Configure hot-reloading for development

### 1.3 Configuration System
- [ ] Implement configuration loading from YAML
- [ ] Define default configuration values
- [ ] Set up environment variable overrides
- [ ] Create sample configuration file

## 2. Backend Core Development

### 2.1 API Framework Setup
- [ ] Set up HTTP server using Chi router
- [ ] Implement middleware for logging, error handling, etc.
- [ ] Create basic health check and version endpoints
- [ ] Set up CORS and security headers

### 2.2 File System Integration
- [ ] Implement file system access abstraction
- [ ] Create functions for reading Markdown files
- [ ] Implement file writing with safe transaction-like approach
- [ ] Set up backup creation before file modifications

### 2.3 Markdown Processing
- [ ] Implement YAML frontmatter parsing
- [ ] Create Markdown body parsing logic
- [ ] Implement functions to extract metadata (tags, properties, etc.)
- [ ] Set up bullet point (event) extraction logic

### 2.4 Daily Note Management
- [ ] Implement logic to create new daily notes
- [ ] Set up template processing for new notes
- [ ] Create functions to manage date-based file naming
- [ ] Implement navigation between daily notes (prev/next)

## 3. Frontend Foundation

### 3.1 Svelte Project Setup
- [ ] Initialize SvelteKit project
- [ ] Configure Tailwind CSS
- [ ] Set up basic component structure
- [ ] Create API client for backend communication

### 3.2 Layout Implementation
- [ ] Create basic three-panel layout (navigation, editor, metadata)
- [ ] Implement responsive design for various screen sizes
- [ ] Set up panel resizing functionality
- [ ] Create collapsible panels

### 3.3 File Navigation Panel
- [ ] Implement file tree component
- [ ] Create calendar view for daily notes
- [ ] Set up file selection handling
- [ ] Implement basic file operations (create, rename, delete)

### 3.4 Markdown Editor Integration
- [ ] Integrate CodeMirror 6
- [ ] Configure basic Markdown syntax highlighting
- [ ] Set up YAML frontmatter handling
- [ ] Implement auto-save functionality

## 4. Database Integration

### 4.1 DuckDB Setup
- [ ] Integrate DuckDB with Go backend
- [ ] Create schema initialization scripts
- [ ] Implement database migration mechanism
- [ ] Set up connection pooling and resource management

### 4.2 Basic Entry Management
- [ ] Implement entry creation/update in database
- [ ] Create functions to query entries by date
- [ ] Set up entry metadata extraction and storage
- [ ] Implement entry deletion and cleanup

### 4.3 Event Processing
- [ ] Create logic to extract events from entries
- [ ] Implement event storage in database
- [ ] Set up event metadata (tags) extraction
- [ ] Create functions to query events by entry ID

## 5. Real-time Synchronization

### 5.1 File Watcher Implementation
- [ ] Set up fsnotify for directory watching
- [ ] Implement debouncing for rapid file changes
- [ ] Create event processing pipeline for file changes
- [ ] Handle file deletion and moves

### 5.2 Database Synchronization
- [ ] Implement incremental indexing logic
- [ ] Create file modification detection based on timestamps
- [ ] Set up background processing for file indexing
- [ ] Implement database cleanup for deleted files

### 5.3 API Endpoints for Sync
- [ ] Create endpoint to trigger manual re-indexing
- [ ] Implement status reporting for indexing process
- [ ] Set up progress tracking for long-running operations
- [ ] Create endpoints for sync status queries

## 6. Integration and Testing

### 6.1 End-to-End Testing
- [ ] Implement integration tests for core workflows
- [ ] Create test fixtures for sample journal entries
- [ ] Set up automated testing in CI pipeline
- [ ] Document testing procedures

### 6.2 UI Refinement
- [ ] Implement loading indicators
- [ ] Create error handling and user notifications
- [ ] Add keyboard shortcuts for common operations
- [ ] Refine styling and visual consistency

### 6.3 Documentation
- [ ] Update API documentation
- [ ] Create user guide for basic operations
- [ ] Document configuration options
- [ ] Prepare deployment instructions

## 7. Deployment and Release

### 7.1 Production Docker Setup
- [ ] Optimize Docker images for production
- [ ] Set up multi-stage builds for smaller images
- [ ] Configure proper logging for production
- [ ] Document volume management for persistent data

### 7.2 Performance Optimization
- [ ] Identify and fix performance bottlenecks
- [ ] Implement caching for frequently accessed data
- [ ] Optimize database queries
- [ ] Configure resource limits appropriately

### 7.3 Release Preparation
- [ ] Create release checklist
- [ ] Prepare release notes
- [ ] Set up version tagging
- [ ] Create user documentation for deployment

## Technical Implementation Details

### Backend Component Architecture
```go
// Main application components
package main
    ├── cmd/                  // Application entry points
    │   └── server/           // Web server command
    ├── internal/             // Internal packages
    │   ├── api/              // REST API handlers
    │   ├── config/           // Configuration management
    │   ├── db/               // DuckDB integration
    │   ├── fs/               // File system operations
    │   ├── markdown/         // Markdown processing
    │   ├── model/            // Data models
    │   └── sync/             // Synchronization logic
    ├── pkg/                  // Public packages
    │   ├── logger/           // Logging utilities
    │   └── util/             // Shared utilities
    └── web/                  // Static web assets
```

### Key Data Structures
```go
// Entry represents a journal entry (daily note)
type Entry struct {
    ID          int64     `json:"id"`
    Date        time.Time `json:"date"`
    FilePath    string    `json:"filePath"`
    FileName    string    `json:"fileName"`
    CreatedAt   time.Time `json:"createdAt"`
    ModifiedAt  time.Time `json:"modifiedAt"`
    Weight      *int      `json:"weight,omitempty"`
    WeatherCond string    `json:"weatherCond,omitempty"`
    WeatherHigh *int      `json:"weatherHigh,omitempty"`
    WeatherLow  *int      `json:"weatherLow,omitempty"`
    Blurb       string    `json:"blurb,omitempty"`
    Tags        []string  `json:"tags,omitempty"`
}

// Event represents a bullet point in a journal entry
type Event struct {
    ID          int64    `json:"id"`
    EntryID     int64    `json:"entryID"`
    Content     string   `json:"content"`
    Tags        []string `json:"tags,omitempty"`
    HasChildren bool     `json:"hasChildren"`
}

// FileChange represents a detected change to a file
type FileChange struct {
    Path     string
    Op       fsnotify.Op
    ModTime  time.Time
}
```

### Core API Endpoints
```
GET    /api/health                  - Health check
GET    /api/entries                 - List all entries
GET    /api/entries/:date           - Get entry by date
POST   /api/entries/:date           - Create/update entry
GET    /api/entries/:date/events    - Get events for entry
POST   /api/reindex                 - Trigger reindexing
GET    /api/reindex/status          - Get reindexing status
```

### Database Schema (Initial)
```sql
-- Entries table
CREATE TABLE IF NOT EXISTS entry (
    id          BIGINT PRIMARY KEY,
    date        DATE UNIQUE,
    file_path   TEXT,
    file_name   TEXT,
    created_at  TIMESTAMP,
    modified_at TIMESTAMP,
    weight      USMALLINT,
    wx_cond     TEXT,
    wx_high     SMALLINT,
    wx_low      SMALLINT,
    blurb       TEXT
);

-- Entry tags junction table
CREATE TABLE IF NOT EXISTS entry_tag (
    entry_id BIGINT,
    tag      TEXT,
    PRIMARY KEY (entry_id, tag)
);

-- Events table (bullet points)
CREATE TABLE IF NOT EXISTS event (
    id           BIGINT PRIMARY KEY,
    entry_id     BIGINT,
    content      TEXT,
    has_children BOOLEAN,
    FOREIGN KEY (entry_id) REFERENCES entry(id) ON DELETE CASCADE
);

-- Event tags junction table
CREATE TABLE IF NOT EXISTS event_tag (
    event_id BIGINT,
    tag      TEXT,
    PRIMARY KEY (event_id, tag)
);
```

## Frontend Component Structure
```
src/
├── lib/
│   ├── components/
│   │   ├── layout/
│   │   │   ├── ThreeColumnLayout.svelte
│   │   │   ├── NavigationPanel.svelte
│   │   │   ├── EditorPanel.svelte
│   │   │   └── MetadataPanel.svelte
│   │   ├── editor/
│   │   │   ├── MarkdownEditor.svelte
│   │   │   └── YamlEditor.svelte
│   │   ├── navigation/
│   │   │   ├── FileTree.svelte
│   │   │   └── Calendar.svelte
│   │   └── common/
│   │       ├── Button.svelte
│   │       └── Loader.svelte
│   ├── api/
│   │   └── client.js
│   └── stores/
│       ├── entries.js
│       └── ui.js
├── routes/
│   ├── +layout.svelte
│   ├── +page.svelte
│   └── entry/[date]/+page.svelte
└── app.html
```

## Development Workflow
1. Set up the project structure and Docker environment
2. Implement core file system operations
3. Create basic API endpoints for CRUD operations
4. Implement DuckDB schema and basic queries
5. Set up Svelte frontend with basic layout
6. Integrate CodeMirror for editing
7. Implement file watching and synchronization
8. Connect frontend and backend for basic operations
9. Add styling and UI refinements
10. Test and optimize the core functionality