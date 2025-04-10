# Phase 1: Core MVP Implementation Work Plan

## Overview

This plan outlines the tasks required to implement the core MVP functionality for the Second Brain application, focusing on basic journaling and viewing capabilities. The goal is to create a locally runnable application that can create, view, and edit daily Markdown notes with full filesystem integration.

## 1. Project Setup and Infrastructure

### 1.1 Development Environment Setup
- [ ] Create project repository with appropriate structure
- [ ] Set up Python virtual environment with Poetry or requirements.txt
- [ ] Configure development tools (linters, formatters, mypy, etc.)
- [ ] Create initial documentation and README

### 1.2 Docker Configuration
- [ ] Create Dockerfile for FastAPI backend
- [ ] Create Dockerfile for Svelte frontend (dev environment)
- [ ] Create docker-compose.yml for local development
- [ ] Set up volume mappings for journal files and database
- [ ] Configure hot-reloading for development

### 1.3 Configuration System
- [ ] Implement configuration loading from YAML using PyYAML
- [ ] Define default configuration values using Pydantic
- [ ] Set up environment variable overrides
- [ ] Create sample configuration file

## 2. Backend Core Development

### 2.1 API Framework Setup
- [ ] Set up FastAPI server with appropriate routers
- [ ] Implement middleware for logging, error handling, etc.
- [ ] Create basic health check and version endpoints
- [ ] Set up CORS and security headers

### 2.2 File System Integration
- [ ] Implement file system access abstraction using pathlib
- [ ] Create functions for reading Markdown files
- [ ] Implement file writing with safe transaction-like approach
- [ ] Set up backup creation before file modifications

### 2.3 Markdown Processing
- [ ] Implement YAML frontmatter parsing with PyYAML
- [ ] Create Markdown body parsing logic using markdown-it-py
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

### 4.1 SQLite Setup
- [ ] Integrate SQLite with FastAPI backend using SQLAlchemy
- [ ] Create schema initialization scripts
- [ ] Implement database migration mechanism using Alembic
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
- [ ] Set up watchdog for directory watching
- [ ] Implement debouncing for rapid file changes
- [ ] Create event processing pipeline for file changes
- [ ] Handle file deletion and moves

### 5.2 Database Synchronization
- [ ] Implement incremental indexing logic
- [ ] Create file modification detection based on timestamps
- [ ] Set up background processing for file indexing using asyncio
- [ ] Implement database cleanup for deleted files

### 5.3 API Endpoints for Sync
- [ ] Create endpoint to trigger manual re-indexing
- [ ] Implement status reporting for indexing process
- [ ] Set up progress tracking for long-running operations
- [ ] Create endpoints for sync status queries

## 6. Integration and Testing

### 6.1 End-to-End Testing
- [ ] Implement integration tests with pytest
- [ ] Create test fixtures for sample journal entries
- [ ] Set up automated testing in CI pipeline
- [ ] Document testing procedures

### 6.2 UI Refinement
- [ ] Implement loading indicators
- [ ] Create error handling and user notifications
- [ ] Add keyboard shortcuts for common operations
- [ ] Refine styling and visual consistency

### 6.3 Documentation
- [ ] Update API documentation using FastAPI's automatic docs
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

```python
# Main application structure
secondbrain/
├── app/                   # FastAPI application
│   ├── api/               # API routes
│   │   ├── __init__.py
│   │   ├── entries.py     # Journal entry endpoints
│   │   ├── events.py      # Event (bullet) endpoints
│   │   ├── search.py      # Search endpoints
│   │   └── query.py       # Natural language query endpoints
│   ├── core/              # Core application logic
│   │   ├── __init__.py
│   │   ├── config.py      # Configuration management
│   │   ├── security.py    # Authentication (if needed)
│   │   └── logging.py     # Logging setup
│   ├── db/                # Database interactions
│   │   ├── __init__.py
│   │   ├── models.py      # SQLAlchemy models
│   │   ├── database.py    # Database connection
│   │   └── sync.py        # DB synchronization logic
│   ├── models/            # Data models (Pydantic)
│   │   ├── __init__.py
│   │   ├── entry.py       # Journal entry models
│   │   ├── event.py       # Event models
│   │   └── search.py      # Search/query models
│   ├── services/          # Business logic services
│   │   ├── __init__.py
│   │   ├── file_service.py     # File operations
│   │   ├── markdown_service.py # Markdown processing
│   │   └── sync_service.py     # Synchronization logic
│   ├── utils/             # Utility functions
│   │   ├── __init__.py
│   │   ├── file_utils.py  # File handling utilities
│   │   └── date_utils.py  # Date handling 
│   ├── main.py            # FastAPI app initialization
│   └── static/            # Static files (if served by FastAPI)
└── tests/                 # Test suite
```

### Key Data Models

```python
# Pydantic models for the API
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

class EntryBase(BaseModel):
    date: datetime
    file_path: str
    file_name: str
    weight: Optional[int] = None
    weather_cond: Optional[str] = None
    weather_high: Optional[int] = None
    weather_low: Optional[int] = None
    blurb: Optional[str] = None
    tags: List[str] = []
    
class EntryCreate(EntryBase):
    pass

class Entry(EntryBase):
    id: int
    created_at: datetime
    modified_at: datetime
    
    class Config:
        orm_mode = True

class EventBase(BaseModel):
    content: str
    has_children: bool = False
    tags: List[str] = []
    
class EventCreate(EventBase):
    entry_id: int
    
class Event(EventBase):
    id: int
    entry_id: int
    
    class Config:
        orm_mode = True

# SQLAlchemy models for the database
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class EntryModel(Base):
    __tablename__ = "entries"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, unique=True, index=True)
    file_path = Column(String)
    file_name = Column(String)
    created_at = Column(DateTime)
    modified_at = Column(DateTime)
    weight = Column(Integer, nullable=True)
    weather_cond = Column(String, nullable=True)
    weather_high = Column(Integer, nullable=True)
    weather_low = Column(Integer, nullable=True)
    blurb = Column(String, nullable=True)
    
    events = relationship("EventModel", back_populates="entry", cascade="all, delete-orphan")
    tags = relationship("EntryTagModel", back_populates="entry", cascade="all, delete-orphan")

class EventModel(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    entry_id = Column(Integer, ForeignKey("entries.id"))
    content = Column(String)
    has_children = Column(Boolean, default=False)
    
    entry = relationship("EntryModel", back_populates="events")
    tags = relationship("EventTagModel", back_populates="event", cascade="all, delete-orphan")

class EntryTagModel(Base):
    __tablename__ = "entry_tags"
    
    entry_id = Column(Integer, ForeignKey("entries.id"), primary_key=True)
    tag = Column(String, primary_key=True)
    
    entry = relationship("EntryModel", back_populates="tags")

class EventTagModel(Base):
    __tablename__ = "event_tags"
    
    event_id = Column(Integer, ForeignKey("events.id"), primary_key=True)
    tag = Column(String, primary_key=True)
    
    event = relationship("EventModel", back_populates="tags")
```

### Core API Endpoints

```
GET    /api/health                  - Health check
GET    /api/entries                 - List all entries
GET    /api/entries/{date}          - Get entry by date
POST   /api/entries/{date}          - Create/update entry
GET    /api/entries/{date}/events   - Get events for entry
POST   /api/reindex                 - Trigger reindexing
GET    /api/reindex/status          - Get reindexing status
```

### Database Schema (Initial)

```sql
-- Entries table
CREATE TABLE IF NOT EXISTS entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE UNIQUE,
    file_path TEXT,
    file_name TEXT,
    created_at TIMESTAMP,
    modified_at TIMESTAMP,
    weight INTEGER,
    weather_cond TEXT,
    weather_high INTEGER,
    weather_low INTEGER,
    blurb TEXT
);

-- Entry tags junction table
CREATE TABLE IF NOT EXISTS entry_tags (
    entry_id INTEGER,
    tag TEXT,
    PRIMARY KEY (entry_id, tag),
    FOREIGN KEY (entry_id) REFERENCES entries(id) ON DELETE CASCADE
);

-- Events table (bullet points)
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_id INTEGER,
    content TEXT,
    has_children BOOLEAN,
    FOREIGN KEY (entry_id) REFERENCES entries(id) ON DELETE CASCADE
);

-- Event tags junction table
CREATE TABLE IF NOT EXISTS event_tags (
    event_id INTEGER,
    tag TEXT,
    PRIMARY KEY (event_id, tag),
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
);
```

### Frontend Component Structure

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
2. Implement core file system operations using Python's pathlib and async handling
3. Create basic FastAPI endpoints for CRUD operations
4. Implement SQLite schema and initial queries with SQLAlchemy
5. Set up Svelte frontend with basic layout
6. Integrate CodeMirror for editing
7. Implement file watching using watchdog
8. Connect frontend and backend for basic operations
9. Add styling and UI refinements
10. Test and optimize the core functionality