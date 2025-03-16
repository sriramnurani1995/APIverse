from fastapi import FastAPI, Query, HTTPException, Request, Path
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import os
from utils.image_processing import resize_image
from utils.paragraph_processing import generate_manual_paragraphs, generate_llm_paragraph
from utils.file_utils import get_downloadable_file_response, save_file
from utils.html_utils import generate_html_page, generate_download_page
from model.model_datastore import model
from utils.helpers import cleanup_old_files
from contextlib import asynccontextmanager
import asyncio
from services.weather_service import get_weather_for_date, get_weather_for_month
from datetime import datetime
from services.gradebook_service import create_course, get_course_header, get_students_by_course
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
from services.starwars_service import (
    get_films, get_people, get_planets, get_species, get_starships, get_vehicles,
    get_film_by_id, get_person_by_id, get_planet_by_id, get_species_by_id, get_starship_by_id, get_vehicle_by_id, check_starwars_data_exists, import_all_starwars_data
)

db = model()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles FastAPI startup & shutdown events."""
    
    db.create_image_mappings()
    print("Image mappings created successfully.")

    # Check if Star Wars data exists, import if needed
    if not check_starwars_data_exists():
        print("Star Wars data not found. Importing data...")
        import_all_starwars_data()
        print("Star Wars data imported successfully.")
    else:
        print("Star Wars data already exists in database.")
        
    # Start cleanup scheduler in the background
    task = asyncio.create_task(cleanup_scheduler())

    yield  

    task.cancel()  

async def cleanup_scheduler():
    """Runs cleanup every 1 hour asynchronously."""
    while True:
        cleanup_old_files("static/downloads", "html")  
        await asyncio.sleep(3600)  

# API description for documentation
description = """
# APIverse - PSU API Hub

A comprehensive API hub for PSU students, providing reliable placeholder, 
weather, gradebook, and Star Wars API endpoints.

## Important Note on Authentication

*This documentation shows the backend API structure. In the actual application, all API endpoints require an API key.*

When using the API:
* API keys must be obtained from the web dashboard after login
* The API key must be included in the URL path according to the patterns shown in the custom documentation
* Authentication is handled by the gateway layer, not shown in this documentation

"""

# Define API documentation metadata
app = FastAPI(
    lifespan=lifespan,
    title="APIverse - PSU API Hub",
    description=description,
    version="1.0.0",
    docs_url=None,
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "APIverse Support",
        "email": "apiverse1@gmail.com",
    },
    license_info={
        "name": "MIT License",
    }
)

# Define Pydantic models for API documentation

class ParagraphResponse(BaseModel):
    paragraphs: List[str] = Field(..., description="List of generated paragraphs")

class WeatherData(BaseModel):
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    temperature: int = Field(..., description="Temperature in Celsius")
    wind: int = Field(..., description="Wind speed in km/h")
    precipitation: int = Field(..., description="Precipitation amount in mm")
    condition: str = Field(..., description="Weather condition (Sunny, Cloudy, Rainy, etc.)")
    description: str = Field(..., description="Detailed weather description")

class CourseComponent(BaseModel):
    type: str = Field(..., description="Component type (Homework, Discussions, FinalExam)")
    component: str = Field(..., description="Component name (e.g., 'Homework 1')")
    marks: float = Field(..., description="Marks obtained")
    totalMarks: int = Field(..., description="Total possible marks")

class StudentGrade(BaseModel):
    courseId: str = Field(..., description="Course identifier")
    studentId: int = Field(..., description="Student identifier")
    name: str = Field(..., description="Student name")
    components: List[CourseComponent] = Field(..., description="List of graded components")
    weightedPercentages: Dict[str, float] = Field(..., description="Weighted percentages per component type")
    finalPercentage: float = Field(..., description="Final percentage grade")
    finalGrade: str = Field(..., description="Final letter grade (A, B, C, D, F)")

class CourseHeader(BaseModel):
    courseId: str = Field(..., description="Course identifier")
    weightage: Dict[str, int] = Field(..., description="Weightage percentage for each component type")
    components: Dict[str, int] = Field(..., description="Number of components for each type")

class CourseCreateRequest(BaseModel):
    courseId: str = Field(..., description="Unique course identifier")
    numStudents: int = Field(20, description="Number of students to generate", ge=1)
    numHomeworks: int = Field(3, description="Number of homework assignments", ge=0)
    numDiscussions: int = Field(2, description="Number of discussion assignments", ge=0)
    numExams: int = Field(1, description="Number of exams", ge=0)
    homeworkWeight: int = Field(40, description="Homework percentage weight", ge=0)
    discussionWeight: int = Field(30, description="Discussion percentage weight", ge=0)
    examWeight: int = Field(30, description="Exam percentage weight", ge=0)

class CourseCreateResponse(BaseModel):
    message: str = Field(..., description="Success message")
    courseId: str = Field(..., description="Course identifier of created course")

# Star Wars Models
class StarWarsFilm(BaseModel):
    title: str = Field(..., description="The title of the film")
    episode_id: int = Field(..., description="The episode number of the film")
    opening_crawl: str = Field(..., description="The opening crawl text of the film")
    director: str = Field(..., description="The director of the film")
    producer: str = Field(..., description="The producer(s) of the film")
    release_date: str = Field(..., description="The release date of the film")
    characters: List[int] = Field(..., description="List of character IDs that appear in the film")
    planets: List[int] = Field(..., description="List of planet IDs that appear in the film")
    starships: List[int] = Field(..., description="List of starship IDs that appear in the film")
    vehicles: List[int] = Field(..., description="List of vehicle IDs that appear in the film")
    species: List[int] = Field(..., description="List of species IDs that appear in the film")

class StarWarsPerson(BaseModel):
    name: str = Field(..., description="The name of the person")
    height: str = Field(..., description="The height of the person in cm")
    mass: str = Field(..., description="The mass of the person in kg")
    hair_color: str = Field(..., description="The hair color of the person")
    skin_color: str = Field(..., description="The skin color of the person")
    eye_color: str = Field(..., description="The eye color of the person")
    birth_year: str = Field(..., description="The birth year of the person in BBY/ABY format")
    gender: str = Field(..., description="The gender of the person")
    homeworld: int = Field(..., description="The ID of the person's homeworld")

class StarWarsPlanet(BaseModel):
    name: str = Field(..., description="The name of the planet")
    rotation_period: str = Field(..., description="The rotation period of the planet in hours")
    orbital_period: str = Field(..., description="The orbital period of the planet in days")
    diameter: str = Field(..., description="The diameter of the planet in km")
    climate: str = Field(..., description="The climate of the planet")
    gravity: str = Field(..., description="The gravity of the planet")
    terrain: str = Field(..., description="The terrain of the planet")
    surface_water: str = Field(..., description="The percentage of the planet covered by water")
    population: str = Field(..., description="The population of the planet")

class StarWarsSpecies(BaseModel):
    name: str = Field(..., description="The name of the species")
    classification: str = Field(..., description="The classification of the species")
    designation: str = Field(..., description="The designation of the species")
    average_height: str = Field(..., description="The average height of the species in cm")
    skin_colors: str = Field(..., description="The skin colors found in the species")
    hair_colors: str = Field(..., description="The hair colors found in the species")
    eye_colors: str = Field(..., description="The eye colors found in the species")
    average_lifespan: str = Field(..., description="The average lifespan of the species")
    homeworld: Optional[int] = Field(None, description="The ID of the species' homeworld")
    language: str = Field(..., description="The language spoken by the species")

# Image placeholder API
@app.get(
    "/{category}/{name}/{width}/{height}/",
    tags=["Images"],
    summary="Get placeholder image",
    responses={
        200: {"content": {"image/jpeg": {}}}, 
        404: {"description": "Image not found"}
    }
)
async def get_placeholder_image(
    category: str = Path(..., description="Image category (e.g., 'cats', 'nature')"),
    name: str = Path(..., description="Specific image name or 'random'"),
    width: int = Path(..., description="Image width in pixels", gt=0, le=2000),
    height: int = Path(..., description="Image height in pixels", gt=0, le=2000)
):
    """
    Retrieve a resized placeholder image.
    
    The image will be resized to the specified dimensions while maintaining aspect ratio.
    Use 'random' as the name parameter to get a random image from the specified category.
    
    Current Available Categories:
    - cat
    - nature
    - dog
    - pup
    - kitten
    
    *Note:* In the actual API, this endpoint is called with an API key in the path:
    /api/{category}/{apikey}/{name}/{width}/{height}/
    """
    image_path = db.get_image_path(category, name)
    
    if not image_path or not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")

    resized_image = resize_image(image_path, width, height)
    return FileResponse(resized_image, media_type="image/jpeg")

# Paragraph generator API
@app.get(
    "/paragraphs",
    tags=["Text Generation"],
    summary="Generate placeholder text",
    response_model=ParagraphResponse
)
async def get_paragraphs(
    type: str = Query("lorem", description="Type of text to generate", 
                     examples={"lorem": {"value": "lorem"}, 
                               "business": {"value": "business"},
                               "tech": {"value": "tech"},
                               "hipster": {"value": "hipster"},
                               "cats": {"value": "cats"},
                               "pup": {"value": "pup"},
                               "llm": {"value": "llm"}}),
    topic: str = Query("random", description="Topic for LLM generation (only for type='llm')"),
    tone: str = Query("neutral", description="Tone for LLM generation (only for type='llm')"),
    length: str = Query("medium", description="Length of paragraphs", 
                       examples={"short": {"value": "short"}, 
                                 "medium": {"value": "medium"},
                                 "long": {"value": "long"}}),
    count: int = Query(3, description="Number of paragraphs to generate", gt=0, le=10),
    format: str = Query("json", description="Output format", 
                       examples={"json": {"value": "json"},
                                 "html": {"value": "html"},
                                 "paragraph_download": {"value": "paragraph_download"}})
):
    """
    Generate placeholder text paragraphs.
    
    This endpoint generates random paragraphs of text based on the specified parameters.
    The text is dynamically generated using patterns and phrases from the selected type. For LLM type, It will generate using given topic and tone value using Gemini LLM models
    
    Different output formats are supported:
    - json: Returns a JSON object with an array of paragraphs
    - html: Returns an HTML page with formatted paragraphs
    - paragraph_download: Returns a downloadable HTML file
    
    *Note:* In the actual API, this endpoint is called with an API key in the path:
    /api/paragraphs/{apikey}?type=lorem&length=medium&count=3&format=json
    """
    if type == "llm":
        paragraphs = [generate_llm_paragraph(topic, tone, length) for _ in range(count)]
    else:
        paragraphs = generate_manual_paragraphs(type, length, count)

    paragraph_styles = {
        ".p1": "text-align: left; font-size: 18px; line-height: 1.6; margin-bottom: 16px; padding: 10px; background: #f8f8f8; border-left: 5px solid #007BFF; border-radius: 4px;",
        ".p2": "text-align: left; font-size: 18px; line-height: 1.6; margin-bottom: 16px; padding: 10px; background: #f0f0f0; border-left: 5px solid #555; border-radius: 4px;",
    }

    if format == "json":
        return JSONResponse(content={"paragraphs": paragraphs}, media_type="application/json")

    html_content = "".join([
        f'<p class="p{(i % 2) + 1}">{paragraph}</p>' for i, paragraph in enumerate(paragraphs)
    ])

    if format == "html":
        return HTMLResponse(content=generate_html_page("Generated Paragraphs", html_content, paragraph_styles))

    if format == "paragraph_download":
        file_path = save_file(content=generate_html_page("Generated Paragraphs", html_content, paragraph_styles), file_extension="html", folder="static/downloads")

        return HTMLResponse(content=generate_download_page("Your Generated Paragraphs HTML", file_path, "generated_paragraphs.html", paragraph_styles))
    raise HTTPException(status_code=400, detail="Invalid format specified")
# File download API
@app.get(
    "/download_file",
    tags=["Utilities"],
    summary="Download generated file"
)
async def download_file(file: str = Query(..., description="Path to the file to download")):
    """
    Serve any generated file for download with the correct MIME type.
    
    This endpoint is primarily used internally by other APIs to serve
    generated files for download.
    """
    return get_downloadable_file_response(file)

# Weather API - Single Date
@app.get(
    "/weather/date/", 
    tags=["Weather"],
    summary="Get weather for a specific date",
    responses={
        200: {"model": WeatherData, "description": "Weather data for the requested date"},
        200: {"content": {"text/html": {"example": "<html>...</html>"}}, "description": "HTML formatted weather data"},
    }
)
async def weather_by_date(
    date: str = Query(None, description="Date in YYYY-MM-DD format", example="2023-07-15"),
    format: str = Query("json", description="Output format", 
                       examples={"json": {"value": "json"},
                                 "html": {"value": "html"}, 
                                 "download": {"value": "download"}})
):
    """
    Retrieve weather data for a specific date.
    
    This endpoint generates consistent random weather data for the specified date.
    The same date will always return the same weather data, allowing for reproducible results.
    
    Weather data includes temperature, wind speed, precipitation, and weather condition.
    The data is appropriately varied based on the season of the provided date.
    
    Available output formats:
    - json: Returns a JSON object with weather data
    - html: Returns an HTML page with formatted weather information
    - download: Returns a downloadable HTML file
    
    If no date is provided, the current date is used.
    
    *Note:* In the actual API, this endpoint is called with an API key in the path:
    /api/weather/date/{apikey}?date=2023-07-15&format=json
    """
    date = date or datetime.now().strftime("%Y-%m-%d")
    return get_weather_for_date(date, format)

# Weather API - Monthly
@app.get(
    "/weather/month/", 
    tags=["Weather"],
    summary="Get weather for an entire month",
    responses={
        200: {"description": "Array of daily weather data for the requested month"},
        200: {"content": {"text/html": {"example": "<html>...</html>"}}, "description": "HTML formatted monthly weather data"},
    }
)
async def weather_by_month(
    month: str = Query(None, description="Month in YYYY-MM format", example="2023-07"), 
    format: str = Query("json", description="Output format", 
                       examples={"json": {"value": "json"},
                                 "html": {"value": "html"}, 
                                 "download": {"value": "download"}})
):
    """
    Retrieve weather data for an entire month.
    
    This endpoint generates consistent random weather data for each day in the specified month.
    The same month will always return the same weather data, allowing for reproducible results.
    
    The data is returned as an array of daily weather data, with each day including
    temperature, wind speed, precipitation, and weather condition.
    
    Available output formats:
    - json: Returns a JSON array with daily weather data
    - html: Returns an HTML page with a formatted weather table
    - download: Returns a downloadable HTML file
    
    If no month is provided, the current month is used.
    
    *Note:* In the actual API, this endpoint is called with an API key in the path:
    /api/weather/month/{apikey}?month=2023-07&format=json
    """
    month = month or datetime.now().strftime("%Y-%m")
    return get_weather_for_month(month, format)

# Course generation API
@app.post(
    "/api/generate_course", 
    tags=["Gradebook"],
    summary="Generate a new course with students",
    response_model=CourseCreateResponse,
)
async def generate_course_post(request: Request, body: CourseCreateRequest):
    """
    Create a new course with randomly generated student data.
    
    This endpoint creates a new course with the specified parameters and
    generates student records with randomized grades for each component.
    
    Note:
    - The sum of component weights (homework, discussion, exam) must equal 100%.
    - Student grades are generated using a normal distribution to create realistic data.
    - For Swagger UI testing, please use courseId "TEST101"
    
    *Note:* In the actual API, this endpoint is called with an API key in the path:
    /api/generate_course/{apikey} with a JSON request body
    """
    # Validate that weights sum to 100%
    
    # For Swagger UI testing, check if courseId is TEST101
    referer = request.headers.get("referer", "")
    if "/docs" in referer and body.courseId != "TEST101":
        raise HTTPException(
            status_code=400, 
            detail='For Swagger testing, please use courseId: "TEST101"'
        )
    
    weight_sum = body.homeworkWeight + body.discussionWeight + body.examWeight
    if weight_sum != 100:
        raise HTTPException(status_code=400, 
                           detail=f"Total weightage must be exactly 100%. Provided: {weight_sum}%")
    
    return create_course(
        body.courseId, 
        body.numStudents, 
        body.numHomeworks, 
        body.numDiscussions, 
        body.numExams, 
        body.homeworkWeight, 
        body.discussionWeight, 
        body.examWeight
    )

@app.get(
    "/api/generate_course", 
    tags=["Gradebook"],
    summary="Generate a new course with students (GET method)",
    response_model=CourseCreateResponse,
)
async def generate_course_get(
    request: Request,
    courseId: str = Query("TEST101", description="Unique course identifier (For Swagger testing, use TEST101)"),
    numStudents: int = Query(20, description="Number of students to generate", ge=1),
    numHomeworks: int = Query(3, description="Number of homework assignments", ge=0),
    numDiscussions: int = Query(2, description="Number of discussion assignments", ge=0),
    numExams: int = Query(1, description="Number of exams", ge=0),
    homeworkWeight: int = Query(40, description="Homework percentage weight", ge=0),
    discussionWeight: int = Query(30, description="Discussion percentage weight", ge=0),
    examWeight: int = Query(30, description="Exam percentage weight", ge=0)
):
    """
    Create a new course with randomly generated student data (GET method).
    
    This endpoint is the GET equivalent of the POST version, allowing course
    creation with query parameters instead of a request body.
    
    Note:
    - The sum of component weights (homework, discussion, exam) must equal 100%.
    - Student grades are generated using a normal distribution to create realistic data.
    - For Swagger UI testing, please use courseId "TEST101"
    
    *Note:* In the actual API, this endpoint is called with an API key in the path:
    /api/generate_course/{apikey}?courseId=CS450&numStudents=20
    """
    
    # For Swagger UI testing, check if courseId is TEST101
    referer = request.headers.get("referer", "")
    if "/docs" in referer and courseId != "TEST101":
        raise HTTPException(
            status_code=400, 
            detail='For Swagger testing, please use courseId: "TEST101"'
        )
        
    # Validate that weights sum to 100%
    weight_sum = homeworkWeight + discussionWeight + examWeight
    if weight_sum != 100:
        raise HTTPException(status_code=400, 
                           detail=f"Total weightage must be exactly 100%. Provided: {weight_sum}%")
    
    return create_course(
        courseId, 
        numStudents, 
        numHomeworks, 
        numDiscussions, 
        numExams, 
        homeworkWeight, 
        discussionWeight, 
        examWeight
    )

# Course header API
@app.get(
    "/api/header/{courseId}", 
    tags=["Gradebook"],
    summary="Get course configuration",
    response_model=CourseHeader,
    responses={
        404: {"description": "Course not found"}
    }
)
async def get_course_header_api(courseId: str = Path(..., description="Course identifier")):
    """
    Retrieve course configuration information.
    
    This endpoint returns the configuration for a specific course, including:
    - Component types (Homework, Discussions, FinalExam)
    - Number of components for each type
    - Weightage for each component type
    
    *Note:* In the actual API, this endpoint is called with an API key in the path:
    /api/header/{apikey}/{courseId}
    """
    course = get_course_header(courseId)
    if not course:
        raise HTTPException(status_code=404, detail=f"Course {courseId} not found.")
    return course

# Gradebook API
@app.get(
    "/api/gradebook/{courseId}", 
    tags=["Gradebook"],
    summary="Get gradebook data",
    responses={
        200: {"description": "List of student grade data"},
        200: {"content": {"text/html": {"example": "<html>...</html>"}}, "description": "HTML formatted gradebook"},
        404: {"description": "Course not found"}
    }
)
async def get_gradebook(
    courseId: str = Path(..., description="Course identifier"),
    format: str = Query("json", description="Output format", 
                       examples={"json": {"value": "json"},
                                 "html": {"value": "html"}, 
                                 "download": {"value": "download"}})
):
    """
    Retrieve gradebook data for a specific course.
    
    This endpoint returns grade data for all students in the specified course.
    For each student, it includes:
    - Personal information (ID, name)
    - Grades for each component (Homeworks, Discussions, Exams)
    - Weighted percentages for each component type
    - Final percentage and letter grade
    
    Available output formats:
    - json: Returns a JSON array with student data
    - html: Returns an HTML page with a formatted gradebook table
    - download: Returns a downloadable HTML file
    
    *Note:* In the actual API, this endpoint is called with an API key in the path:
    /api/gradebook/{apikey}/{courseId}?format=json
    """
    students = get_students_by_course(courseId)
    course = get_course_header(courseId)
    
    if not course:
        raise HTTPException(status_code=404, detail=f"Course {courseId} not found.")

    if format == "json":
        return students

    gradebook_styles = {
        "body": "font-family: Arial, sans-serif; margin: 20px; background-color: #f4f4f4;",
        "h2": "text-align: center; color: #333;",
        "table": "width: 100%; border-collapse: collapse; margin-top: 20px; background: white;",
        "th, td": "padding: 12px; text-align: center; border: 1px solid black;",
        "th": "background-color: darkviolet; color: white; font-size: 16px;",
        "td": "font-size: 14px;",
        ".A": "background-color: #d4edda;",
        ".B": "background-color: #c3e6cb;",
        ".C": "background-color: #ffeeba;",
        ".D": "background-color: #f5c6cb;",
        ".F": "background-color: #f8d7da;",
    }

    component_headers = ""
    for comp_type, count in course["components"].items():
        for i in range(1, count + 1):
            component_headers += f"<th>{comp_type} {i}</th>"
        component_headers += f"<th>{comp_type} Weighted %</th>"

    html_table_content = f"""
    <table>
        <tr><th>Student ID</th><th>Name</th>{component_headers}<th>Final Percentage</th><th>Grade</th></tr>
    """
    
    for student in students:
        final_grade = student.get('finalGrade', 'N/A')
        grade_class = f' class="{final_grade}"' if final_grade in ["A", "B", "C", "D", "F"] else ""

        row_values = ""
        weighted_percentages = student.get("weightedPercentages", {})

        for comp_type, count in course["components"].items():
            marks_list = [comp['marks'] for comp in student['components'] if comp['type'] == comp_type]
            row_values += "".join(f"<td>{mark}</td>" for mark in marks_list)
            row_values += f"<td>{weighted_percentages.get(comp_type, 'N/A')}%</td>"

        html_table_content += f"""
        <tr{grade_class}>
        <td>{student['studentId']}</td>
        <td>{student['name']}</td>
        {row_values}
        <td>{student.get('finalPercentage', 'N/A')}%</td>
        <td>{final_grade}</td>
        </tr>"""
    
    html_table_content += "</table>"

    html_content = generate_html_page(f"Gradebook for {courseId}", html_table_content, gradebook_styles)

    if format == "download":
        file_path = save_file(content=html_content, file_extension="html", folder="static/downloads")
        return HTMLResponse(content=generate_download_page("Your Gradebook HTML", file_path, f"{courseId}_gradebook.html", gradebook_styles))

    return HTMLResponse(content=html_content)

# Star Wars API endpoints
@app.get(
    "/starwars/films",
    tags=["Star Wars API"],
    summary="Get Star Wars films",
    responses={
        200: {"description": "List of Star Wars films"},
        200: {"content": {"text/html": {"example": "<html>...</html>"}}, "description": "HTML formatted film data"}
    }
)
async def starwars_films(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of records to return"),
    search: Optional[str] = Query(None, description="Search term for film titles"),
    format: str = Query("json", description="Output format", 
                        examples={"json": {"value": "json"},
                                 "html": {"value": "html"}, 
                                 "download": {"value": "download"}})
):
    """
    Get Star Wars films with pagination and optional search.
    
    This endpoint returns a list of Star Wars films with support for:
    - Pagination (skip and limit parameters)
    - Text search on film titles
    - Multiple output formats
    
    *Note:* In the actual API, this endpoint is called with an API key in the path:
    /api/starwars/films/{apikey}?skip=0&limit=10&search=hope&format=json
    """
    return await get_films(skip, limit, search, format)

@app.get(
    "/starwars/people",
    tags=["Star Wars API"],
    summary="Get Star Wars people",
    responses={
        200: {"description": "List of Star Wars people"},
        200: {"content": {"text/html": {"example": "<html>...</html>"}}, "description": "HTML formatted people data"}
    }
)
async def starwars_people(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of records to return"),
    search: Optional[str] = Query(None, description="Search term for people names"),
    format: str = Query("json", description="Output format", 
                        examples={"json": {"value": "json"},
                                  "html": {"value": "html"}, 
                                  "download": {"value": "download"}})
):
    """
    Get Star Wars people with pagination and optional search.
    
    This endpoint returns a list of Star Wars characters with support for:
    - Pagination (skip and limit parameters)
    - Text search on character names
    - Multiple output formats
    
    *Note:* In the actual API, this endpoint is called with an API key in the path:
    /api/starwars/people/{apikey}?skip=0&limit=10&search=luke&format=json
    """
    return await get_people(skip, limit, search, format)

@app.get(
    "/starwars/people/{person_id}",
    tags=["Star Wars API"],
    summary="Get a specific Star Wars character",
    responses={
        200: {"description": "Star Wars character details"},
        200: {"content": {"text/html": {"example": "<html>...</html>"}}, "description": "HTML formatted character details"},
        404: {"description": "Character not found"}
    }
)
async def starwars_person_by_id(
    person_id: int = Path(..., description="The ID of the character to retrieve"),
    format: str = Query("json", description="Output format", 
                        examples={"json": {"value": "json"},
                                  "html": {"value": "html"}, 
                                  "download": {"value": "download"}})
):
    """
    Get details for a specific Star Wars character by ID.
    
    This endpoint returns detailed information about a single Star Wars character,
    including name, homeworld, physical attributes, and other related data.
    
    *Note:* In the actual API, this endpoint is called with an API key in the path:
    /api/starwars/people/{person_id}/{apikey}?format=json
    """
    return await get_person_by_id(person_id, format)

@app.get(
    "/starwars/planets",
    tags=["Star Wars API"],
    summary="Get Star Wars planets",
    responses={
        200: {"description": "List of Star Wars planets"},
        200: {"content": {"text/html": {"example": "<html>...</html>"}}, "description": "HTML formatted planet data"}
    }
)
async def starwars_planets(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of records to return"),
    search: Optional[str] = Query(None, description="Search term for planet names"),
    format: str = Query("json", description="Output format", 
                        examples={"json": {"value": "json"},
                                  "html": {"value": "html"}, 
                                  "download": {"value": "download"}})
):
    """
    Get Star Wars planets with pagination and optional search.
    
    This endpoint returns a list of Star Wars planets with support for:
    - Pagination (skip and limit parameters)
    - Text search on planet names
    - Multiple output formats
    
    *Note:* In the actual API, this endpoint is called with an API key in the path:
    /api/starwars/planets/{apikey}?skip=0&limit=10&search=tatooine&format=json
    """
    return await get_planets(skip, limit, search, format)

@app.get(
    "/starwars/species",
    tags=["Star Wars API"],
    summary="Get Star Wars species",
    responses={
        200: {"description": "List of Star Wars species"},
        200: {"content": {"text/html": {"example": "<html>...</html>"}}, "description": "HTML formatted species data"}
    }
)
async def starwars_species(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of records to return"),
    search: Optional[str] = Query(None, description="Search term for species names"),
    format: str = Query("json", description="Output format", 
                        examples={"json": {"value": "json"},
                                  "html": {"value": "html"}, 
                                  "download": {"value": "download"}})
):
    """
    Get Star Wars species with pagination and optional search.
    
    This endpoint returns a list of Star Wars species with support for:
    - Pagination (skip and limit parameters)
    - Text search on species names
    - Multiple output formats
    
    *Note:* In the actual API, this endpoint is called with an API key in the path:
    /api/starwars/species/{apikey}?skip=0&limit=10&search=wookie&format=json
    """
    return await get_species(skip, limit, search, format)

@app.get(
    "/starwars/species/{species_id}",
    tags=["Star Wars API"],
    summary="Get a specific Star Wars species",
    responses={
        200: {"description": "Star Wars species details"},
        200: {"content": {"text/html": {"example": "<html>...</html>"}}, "description": "HTML formatted species details"},
        404: {"description": "Species not found"}
    }
)
async def starwars_species_by_id(
    species_id: int = Path(..., description="The ID of the species to retrieve"),
    format: str = Query("json", description="Output format", 
                        examples={"json": {"value": "json"},
                                  "html": {"value": "html"}, 
                                  "download": {"value": "download"}})
):
    """
    Get details for a specific Star Wars species by ID.
    
    This endpoint returns detailed information about a single Star Wars species,
    including name, classification, homeworld, language, and other related data.
    
    *Note:* In the actual API, this endpoint is called with an API key in the path:
    /api/starwars/species/{species_id}/{apikey}?format=json
    """
    return await get_species_by_id(species_id, format)

@app.get(
    "/starwars/starships",
    tags=["Star Wars API"],
    summary="Get Star Wars starships",
    responses={
        200: {"description": "List of Star Wars starships"},
        200: {"content": {"text/html": {"example": "<html>...</html>"}}, "description": "HTML formatted starship data"}
    }
)
async def starwars_starships(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of records to return"),
    search: Optional[str] = Query(None, description="Search term for starship names"),
    format: str = Query("json", description="Output format", 
                        examples={"json": {"value": "json"},
                                  "html": {"value": "html"}, 
                                  "download": {"value": "download"}})
):
    """
    Get Star Wars starships with pagination and optional search.
    
    This endpoint returns a list of Star Wars starships with support for:
    - Pagination (skip and limit parameters)
    - Text search on starship names
    - Multiple output formats
    
    *Note:* In the actual API, this endpoint is called with an API key in the path:
    /api/starwars/starships/{apikey}?skip=0&limit=10&search=falcon&format=json
    """
    return await get_starships(skip, limit, search, format)

@app.get(
    "/starwars/vehicles",
    tags=["Star Wars API"],
    summary="Get Star Wars vehicles",
    responses={
        200: {"description": "List of Star Wars vehicles"},
        200: {"content": {"text/html": {"example": "<html>...</html>"}}, "description": "HTML formatted vehicle data"}
    }
)
async def starwars_vehicles(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of records to return"),
    search: Optional[str] = Query(None, description="Search term for vehicle names"),
    format: str = Query("json", description="Output format", 
                        examples={"json": {"value": "json"},
                                  "html": {"value": "html"}, 
                                  "download": {"value": "download"}})
):
    """
    Get Star Wars vehicles with pagination and optional search.
    
    This endpoint returns a list of Star Wars vehicles with support for:
    - Pagination (skip and limit parameters)
    - Text search on vehicle names
    - Multiple output formats
    
    *Note:* In the actual API, this endpoint is called with an API key in the path:
    /api/starwars/vehicles/{apikey}?skip=0&limit=10&search=speeder&format=json
    """
    return await get_vehicles(skip, limit, search, format)

@app.get(
    "/starwars/vehicles/{vehicle_id}",
    tags=["Star Wars API"],
    summary="Get a specific Star Wars vehicle",
    responses={
        200: {"description": "Star Wars vehicle details"},
        200: {"content": {"text/html": {"example": "<html>...</html>"}}, "description": "HTML formatted vehicle details"},
        404: {"description": "Vehicle not found"}
    }
)
async def starwars_vehicle_by_id(
    vehicle_id: int = Path(..., description="The ID of the vehicle to retrieve"),
    format: str = Query("json", description="Output format", 
                        examples={"json": {"value": "json"},
                                  "html": {"value": "html"}, 
                                  "download": {"value": "download"}})
):
    """
    Get details for a specific Star Wars vehicle by ID.
    
    This endpoint returns detailed information about a single Star Wars vehicle,
    including name, model, manufacturer, cost, and other related data.
    
    *Note:* In the actual API, this endpoint is called with an API key in the path:
    /api/starwars/vehicles/{vehicle_id}/{apikey}?format=json
    """
    return await get_vehicle_by_id(vehicle_id, format)

# Static files and custom Swagger UI
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui():
    """Custom Swagger UI documentation page."""
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="APIverse API Documentation",
        swagger_ui_parameters={"tryItOutEnabled": True},  # Keep "Try it out"
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css"
    )