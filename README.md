# APIverse

A comprehensive API hub for PSU students, providing reliable placeholder, weather, gradebook, and Star Wars API endpoints with secure authentication.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technical Architecture](#technical-architecture)
- [Project Structure](#project-structure)
- [API Reference](#api-reference)
  - [Placeholder Image API](#placeholder-image-api)
  - [Paragraph API](#paragraph-api)
  - [Weather API](#weather-api)
  - [Gradebook API](#gradebook-api)
- [Authentication](#authentication)
- [Installation & Setup](#installation--setup)
- [Local Development](#local-development)
- [Deployment](#deployment)
- [Security Considerations](#security-considerations)
- [Contributing](#contributing)
- [Example API Usage](#example-api-usage)

## Overview

APIverse is a Software Engineering Project that provides PSU students with a local API hub, replicating useful placeholder APIs, weather data APIs, gradebook management, and Star Wars API endpoints. The system ensures reliability, security with API key authentication, and is designed for cost-effective cloud deployment using Docker and Google Cloud Platform's Cloud Run.

## Features

### Core Features

- **User Authentication**: Secure signup, login, and account management for PDX users
- **API Key Management**: Generation, validation, and revocation of API keys
- **Placeholder APIs**:
  - Image generation with customizable dimensions and categories
  - Paragraph text generation with variable themes, lengths, and counts
- **Weather API**:
  - Daily weather forecasts with randomized but reproducible data
  - Monthly weather data with appropriate seasonal variations
- **Gradebook API**:
  - Course creation with customizable grading components
  - Student grade generation with realistic distributions
  - Multiple output formats (JSON, HTML, downloadable)
- **Star Wars API**: Re-implementation of swapi.dev with enhanced data

### Technical Features

- Two-tier architecture (Flask frontend, FastAPI backend)
- Google Cloud Datastore for persistent storage
- Secure API key generation with salted hashing
- Caching system for optimized performance
- File generation and download capabilities
- Responsive web interface

## Technical Architecture

APIverse employs a two-tier architecture:

1. **Frontend/Gateway Layer** (Flask):

   - User authentication and session management
   - API key generation and validation
   - Request routing and endpoint security
   - Web interface for user interaction

2. **Backend/Service Layer** (FastAPI):

   - Core API functionality
   - Data processing and generation
   - Resource transformation
   - File handling and caching

3. **Data Layer** (Google Cloud Datastore):
   - User accounts and authentication
   - API key storage and validation
   - Persistent data for APIs
   - Object mapping and querying

![Architecture Diagram](architecture_diagram.svg)

## Project Structure

```
src/
├── app.py                   # Main Flask application entry point
├── run.py                   # Development runner script
├── app/                     # Flask view controllers
│   ├── __init__.py
│   ├── dashboard.py         # API key management interface
│   ├── index.py             # Homepage controller
│   ├── login.py             # User authentication
│   ├── logout.py            # Session management
│   └── signup.py            # User registration
├── model/                   # Data access layer
│   ├── __init__.py
│   └── model_datastore.py   # Google Cloud Datastore integration
├── services/                # API implementations
│   ├── __init__.py
│   ├── fastapi_service.py   # Main FastAPI application
│   ├── gradebook_service.py # Course and student grade generation
│   └── weather_service.py   # Weather data generation
├── static/                  # Web assets
│   ├── styles.css           # Global stylesheet
│   └── templates/           # HTML templates
│       ├── dashboard.html   # API key management view
│       ├── index.html       # Homepage view
│       ├── layout.html      # Base template
│       ├── login.html       # Login form
│       └── signup.html      # Registration form
└── utils/                   # Shared utilities
    ├── __init__.py
    ├── api_key_generation.py # API key management
    ├── caching.py           # Memory caching system
    ├── file_utils.py        # File handling utilities
    ├── grade_utils.py       # Grade calculation functions
    ├── helpers.py           # Miscellaneous helper functions
    ├── html_utils.py        # HTML generation utilities
    ├── image_processing.py  # Image resizing and caching
    └── paragraph_processing.py # Text generation utilities
```


## API Reference

### Placeholder Image API

Generate placeholder images with custom dimensions.

**Endpoint**: `/api/<category>/<apikey>/<name>/<width>/<height>/`

**Methods**: GET

**URL Parameters**:

- `category`: Image category (e.g., 'cats', 'nature')
- `apikey`: Your API key
- `name`: Specific image name or 'random'
- `width`: Image width in pixels
- `height`: Image height in pixels

**Response**: JPEG image

**Example**: `/api/cats/YOUR_API_KEY/random/300/200/`

**Sample Response**:
Returns a JPEG image file of a cat with dimensions 300x200 pixels.

### Paragraph API

Generate placeholder text paragraphs.

**Endpoint**: `/api/paragraphs/<apikey>`

**Methods**: GET

**URL Parameters**:

- `apikey`: Your API key

**Query Parameters**:

- `type`: Text type ('lorem', 'business', 'tech', 'hipster', 'cats', 'pup') - default: 'lorem'
- `length`: Paragraph length ('short', 'medium', 'long') - default: 'medium'
- `count`: Number of paragraphs - default: 3
- `format`: Output format ('json', 'html', 'paragraph_download') - default: 'json'

**Response**:

- JSON object with paragraphs array
- HTML page with formatted paragraphs
- Downloadable HTML file

**Example**: `/api/paragraphs/YOUR_API_KEY?type=business&length=short&count=2&format=json`

**Sample Response**:

```json
{
  "paragraphs": [
    "Leverage key deliverables. Synergize core competencies. Maximize ROI. Empower team collaboration. Scale vertical markets drive innovation optimize operational efficiencies.",
    "Engage stakeholders. Pivot strategy disrupt traditional paradigms. Drive innovation. Optimize operational efficiencies. Leverage key deliverables synergize core competencies."
  ]
}
```


### Weather API

Generate random but consistent weather data.

#### Single Date Weather

**Endpoint**: `/api/weather/date/<apikey>`

**Methods**: GET

**URL Parameters**:

- `apikey`: Your API key

**Query Parameters**:

- `date`: Date in YYYY-MM-DD format - default: current date
- `format`: Output format ('json', 'html', 'download') - default: 'json'

**Response**:

- JSON object with weather data
- HTML page with formatted weather data
- Downloadable HTML file

**Example**: `/api/weather/date/YOUR_API_KEY?date=2023-06-15&format=json`

**Sample Response**:

```json
{
  "date": "2023-06-15",
  "temperature": 28,
  "wind": 12,
  "precipitation": 5,
  "condition": "Sunny",
  "description": "Clear skies and warm temperatures."
}
```

#### Monthly Weather

**Endpoint**: `/api/weather/month/<apikey>`

**Methods**: GET

**URL Parameters**:

- `apikey`: Your API key

**Query Parameters**:

- `month`: Month in YYYY-MM format - default: current month
- `format`: Output format ('json', 'html', 'download') - default: 'json'

**Response**:

- JSON array with daily weather data
- HTML page with formatted weather table
- Downloadable HTML file

**Example**: `/api/weather/month/YOUR_API_KEY?month=2023-06&format=json`

**Sample Response**:

```json
[
  {
    "date": "2023-06-01",
    "temperature": 26,
    "wind": 8,
    "precipitation": 0,
    "condition": "Sunny",
    "description": "Clear skies and warm temperatures."
  },
  {
    "date": "2023-06-02",
    "temperature": 29,
    "wind": 12,
    "precipitation": 3,
    "condition": "Cloudy",
    "description": "Overcast skies with mild temperatures."
  }
  // ... additional days of the month
]
```

**HTML Format Example**: `/api/weather/month/YOUR_API_KEY?month=2023-06&format=html`

### Gradebook API

Generate and manage course gradebooks.

#### Generate Course

**Endpoint**: `/api/generate_course/<apikey>`

**Methods**: GET, POST

**URL Parameters**:

- `apikey`: Your API key

**Query/Body Parameters**:

- `courseId`: Unique course identifier (required)
- `numStudents`: Number of students - default: 20
- `numHomeworks`: Number of homework assignments - default: 3
- `numDiscussions`: Number of discussion assignments - default: 2
- `numExams`: Number of exams - default: 1
- `homeworkWeight`: Homework percentage weight - default: 40
- `discussionWeight`: Discussion percentage weight - default: 30
- `examWeight`: Exam percentage weight - default: 30

**Response**: JSON object with course creation confirmation

**Example**: `/api/generate_course/YOUR_API_KEY?courseId=CS450&numStudents=25`

**Sample Response**:

```json
{
  "message": "Course and students generated successfully",
  "courseId": "CS450"
}
```

#### Get Course Header

**Endpoint**: `/api/header/<apikey>/<courseId>`

**Methods**: GET

**URL Parameters**:

- `apikey`: Your API key
- `courseId`: Course identifier

**Response**: JSON object with course configuration

**Example**: `/api/header/YOUR_API_KEY/CS450`

**Sample Response**:

```json
{
  "courseId": "CS450",
  "weightage": {
    "Homework": 40,
    "Discussions": 30,
    "FinalExam": 30
  },
  "components": {
    "Homework": 3,
    "Discussions": 2,
    "FinalExam": 1
  }
}
```

#### Get Gradebook

**Endpoint**: `/api/gradebook/<apikey>/<courseId>`

**Methods**: GET

**URL Parameters**:

- `apikey`: Your API key
- `courseId`: Course identifier

**Query Parameters**:

- `format`: Output format ('json', 'html', 'download') - default: 'json'

**Response**:

- JSON array with student data
- HTML page with formatted gradebook
- Downloadable HTML file

**Example**: `/api/gradebook/YOUR_API_KEY/CS450?format=json`

**Sample Response**:

```json
[
  {
    "courseId": "CS450",
    "studentId": 1,
    "name": "Jane Smith",
    "components": [
      {
        "type": "Homework",
        "component": "Homework 1",
        "marks": 92,
        "totalMarks": 100
      },
      {
        "type": "Homework",
        "component": "Homework 2",
        "marks": 88,
        "totalMarks": 100
      },
      {
        "type": "Homework",
        "component": "Homework 3",
        "marks": 95,
        "totalMarks": 100
      },
      {
        "type": "Discussions",
        "component": "Discussions 1",
        "marks": 90,
        "totalMarks": 100
      },
      {
        "type": "Discussions",
        "component": "Discussions 2",
        "marks": 85,
        "totalMarks": 100
      },
      {
        "type": "FinalExam",
        "component": "FinalExam 1",
        "marks": 87,
        "totalMarks": 100
      }
    ],
    "weightedPercentages": {
      "Homework": 36.67,
      "Discussions": 26.25,
      "FinalExam": 26.1
    },
    "finalPercentage": 89.02,
    "finalGrade": "B"
  }
  // ... additional students
]
```

**HTML Format Example**: `/api/gradebook/YOUR_API_KEY/CS450?format=html`

README structure TODO

## Authentication

### User Registration

### API Key Management

### API Key Security

## Installation & Setup

### Prerequisites

### Environment Setup

## Local Development

## Deployment

### Google Cloud Platform (GCP)

## Security Considerations

## Contributing

## Example API Usage

### Python

### JavaScript
