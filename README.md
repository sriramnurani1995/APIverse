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

#### Single Date Weather

#### Monthly Weather

### Gradebook API

#### Generate Course

#### Get Course Header

#### Get Gradebook

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
