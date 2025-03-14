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

## Authentication

### User Registration

1. Visit `/signup`
2. Enter your full name, PDX email address, and password
3. Upon successful registration, you'll be redirected to the dashboard

### API Key Management

1. Log in to your account at `/login`
2. Navigate to the dashboard
3. Click "Generate" to create a new API key
4. Copy the key within 60 seconds (keys are hidden after this time)
5. Use the key in your API requests as shown in the API Reference
6. Revoke keys that are no longer needed

### API Key Security

- Keys are stored as salted SHA-256 hashes
- Keys expire after 30 days
- Keys can be revoked at any time
- Access is restricted to PDX email addresses

## Installation & Setup

### Prerequisites

- Python 3.8+
- Google Cloud SDK (for Datastore)
- Google Cloud Datastore credentials

### Environment Setup

1. Clone the repository:

   ```
   git clone https://github.com/your-org/apiverse.git
   cd apiverse
   ```

2. Create and activate a virtual environment:

   ```
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:

   ```
   export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/credentials.json"
   export FASTAPI_URL="http://localhost:8000"  # For local development
   ```

5. Initialize the Datastore emulator (for local development):
   ```
   gcloud beta emulators datastore start --no-store-on-disk
   ```

## Local Development

To run the application locally:

```
python src/run.py
```

This will start both the Flask application (on port 5000) and the FastAPI service (on port 8000).

Access the web interface at http://localhost:5000

## Deployment

### Google Cloud Platform (GCP)

1. Build the Docker container:

   ```
   docker build -t apiverse .
   ```

2. Push to Google Container Registry:

   ```
   docker tag apiverse gcr.io/[PROJECT_ID]/apiverse
   docker push gcr.io/[PROJECT_ID]/apiverse
   ```

3. Deploy to Cloud Run:
   ```
   gcloud run deploy apiverse --image gcr.io/[PROJECT_ID]/apiverse --platform managed
   ```

## Security Considerations

- API keys are one-way hashed and cannot be recovered if lost
- User passwords are stored using secure hashing (werkzeug.security)
- Keys expire automatically after 30 days
- PDX email restriction prevents unauthorized access
- API endpoints validate key ownership before processing
- Downloaded files are automatically cleaned up after 1 hour

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## Example API Usage

Here are code examples of how to use the APIs in different programming languages:

### Python

```python
import requests

# Your API key
API_KEY = "your_api_key_here"

# Example: Get weather data for a specific date
response = requests.get(f"https://apiverse.example.com/api/weather/date/{API_KEY}?date=2023-06-15")
weather_data = response.json()
print(f"Temperature on June 15: {weather_data['temperature']}°C")

# Example: Generate placeholder paragraphs
response = requests.get(
    f"https://apiverse.example.com/api/paragraphs/{API_KEY}",
    params={"type": "tech", "count": 3, "length": "short"}
)
paragraphs = response.json()["paragraphs"]
for i, paragraph in enumerate(paragraphs, 1):
    print(f"Paragraph {i}: {paragraph[:50]}...")
```

### JavaScript

```javascript
// Your API key
const API_KEY = "your_api_key_here";

// Example: Get gradebook data
fetch(`https://apiverse.example.com/api/gradebook/${API_KEY}/CS450`)
  .then((response) => response.json())
  .then((students) => {
    console.log(`Number of students: ${students.length}`);

    // Calculate class average
    const classAverage =
      students.reduce((sum, student) => sum + student.finalPercentage, 0) /
      students.length;
    console.log(`Class average: ${classAverage.toFixed(2)}%`);
  })
  .catch((error) => console.error("Error fetching gradebook:", error));

// Example: Generate course with custom weights
const courseData = {
  courseId: "CS401",
  numStudents: 30,
  homeworkWeight: 50,
  discussionWeight: 20,
  examWeight: 30,
};

fetch(`https://apiverse.example.com/api/generate_course/${API_KEY}`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify(courseData),
})
  .then((response) => response.json())
  .then((data) => console.log(data.message))
  .catch((error) => console.error("Error generating course:", error));
```
