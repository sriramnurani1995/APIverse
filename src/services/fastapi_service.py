from fastapi import FastAPI, Query, HTTPException,Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
import os
from utils.image_processing import resize_image
from utils.paragraph_processing import generate_paragraphs
from utils.file_utils import get_downloadable_file_response, save_file
from utils.html_utils import generate_html_page, generate_download_page
from model.model_datastore import model
from utils.helpers import cleanup_old_files
from contextlib import asynccontextmanager
import asyncio
from services.weather_service import get_weather_for_date, get_weather_for_month
from datetime import datetime
from services.gradebook_service import create_course, get_course_header, get_students_by_course
from services.starwars_service import (
    get_films, get_people, get_planets, get_species, get_starships, get_vehicles,
    get_film_by_id, get_person_by_id, get_planet_by_id, get_species_by_id, get_starship_by_id, get_vehicle_by_id, check_starwars_data_exists, import_all_starwars_data
)
from typing import Optional


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

app = FastAPI(lifespan=lifespan)  




@app.get("/{category}/{name}/{width}/{height}/")
def get_placeholder_image(category: str, name: str, width: int, height: int):
    image_path = db.get_image_path(category, name)
    
    if not image_path or not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")

    resized_image = resize_image(image_path, width, height)
    return FileResponse(resized_image, media_type="image/jpeg")

@app.get("/paragraphs")
def get_paragraphs(
    type: str = Query("lorem"),
    length: str = Query("medium"),
    count: int = Query(3),
    format: str = Query("json")
):
    """FastAPI Endpoint for Placeholder Paragraphs in JSON, HTML, or Downloadable HTML."""
    paragraphs = generate_paragraphs(type, length, count)


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
    
        file_path = save_file(content=generate_html_page("Generated Paragraphs", html_content, paragraph_styles),file_extension="html", folder="static/downloads")

        return HTMLResponse(content=generate_download_page("Your Generated Paragraphs HTML", file_path, "generated_paragraphs.html", paragraph_styles))


@app.get("/download_file")
def download_file(file: str):
    """Serve any generated file for download with correct MIME type."""
    return get_downloadable_file_response(file)

@app.get("/weather/date/")
def weather_by_date(date: str = Query(None), format: str = Query("json")):
    date = date or datetime.now().strftime("%Y-%m-%d")
    return get_weather_for_date(date, format)

@app.get("/weather/month/")
def weather_by_month(month: str = Query(None), format: str = Query("json")):
    month = month or datetime.now().strftime("%Y-%m")
    return get_weather_for_month(month, format)

@app.api_route("/api/generate_course", methods=["GET", "POST"])
async def generate_course(
    request: Request,
    courseId: str = Query(None),
    numStudents: int = Query(20, ge=1),
    numHomeworks: int = Query(3, ge=0),
    numDiscussions: int = Query(2, ge=0),
    numExams: int = Query(1, ge=0),
    homeworkWeight: int = Query(40, ge=0),
    discussionWeight: int = Query(30, ge=0),
    examWeight: int = Query(30, ge=0)
):
    """
    Allows both GET (with query parameters) and POST (with JSON) for course creation.
    """

   
    if request.method == "POST":
        try:
            data = await request.json()
            courseId = data.get("courseId")
            numStudents = data.get("numStudents", 20)
            numHomeworks = data.get("numHomeworks", 3)
            numDiscussions = data.get("numDiscussions", 2)
            numExams = data.get("numExams", 1)
            homeworkWeight = data.get("homeworkWeight", 40)
            discussionWeight = data.get("discussionWeight", 30)
            examWeight = data.get("examWeight", 30)
        except Exception:
            return JSONResponse(status_code=400, content={"error": "Invalid JSON payload"})

   
    if not courseId:
        return JSONResponse(status_code=422, content={"error": "courseId is required"})

    
    return create_course(courseId, numStudents, numHomeworks, numDiscussions, numExams, homeworkWeight, discussionWeight, examWeight)

@app.get("/api/header/{courseId}")
def get_course_header_api(courseId: str):
    course = get_course_header(courseId)
    if not course:
        raise HTTPException(status_code=404, detail=f"Course {courseId} not found.")
    return course

@app.get("/api/gradebook/{courseId}")
def get_gradebook(courseId: str, format: str = "json"):
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
        component_headers += f"<th>{comp_type} Weighted %</th>"  # Adding weighted percentage column

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

@app.get("/starwars/films",tags=["Star Wars API"])
async def starwars_films(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    format: str = Query("json")
):
    """Get Star Wars films with pagination and optional search."""
    return await get_films(skip, limit, search, format)

@app.get("/starwars/films/{film_id}",tags=["Star Wars API"])
async def starwars_film_by_id(
    film_id: int,
    format: str = Query("json")
):
    """Get a specific Star Wars film by ID."""
    return await get_film_by_id(film_id, format)

@app.get("/starwars/people",tags=["Star Wars API"])
async def starwars_people(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    format: str = Query("json")
):
    """Get Star Wars people with pagination and optional search."""
    return await get_people(skip, limit, search, format)

@app.get("/starwars/people/{person_id}",tags=["Star Wars API"])
async def starwars_person_by_id(
    person_id: int,
    format: str = Query("json")
):
    """Get a specific Star Wars person by ID."""
    return get_person_by_id(person_id, format)

@app.get("/starwars/planets",tags=["Star Wars API"])
async def starwars_planets(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    format: str = Query("json")
):
    """Get Star Wars planets with pagination and optional search."""
    return await get_planets(skip, limit, search, format)

@app.get("/starwars/planets/{planet_id}",tags=["Star Wars API"])
async def starwars_planet_by_id(
    planet_id: int,
    format: str = Query("json")
):
    """Get a specific Star Wars planet by ID."""
    return await get_planet_by_id(planet_id, format)

@app.get("/starwars/species",tags=["Star Wars API"])
async def starwars_species(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    format: str = Query("json")
):
    """Get Star Wars species with pagination and optional search."""
    return await get_species(skip, limit, search, format)

@app.get("/starwars/species/{species_id}",tags=["Star Wars API"])
async def starwars_species_by_id(
    species_id: int,
    format: str = Query("json")
):
    """Get a specific Star Wars species by ID."""
    return await get_species_by_id(species_id, format)

@app.get("/starwars/starships",tags=["Star Wars API"])
async def starwars_starships(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    format: str = Query("json")
):
    """Get Star Wars starships with pagination and optional search."""
    return await get_starships(skip, limit, search, format)

@app.get("/starwars/starships/{starship_id}",tags=["Star Wars API"])
async def starwars_starship_by_id(
    starship_id: int,
    format: str = Query("json")
):
    """Get a specific Star Wars starship by ID."""
    return await get_starship_by_id(starship_id, format)

@app.get("/starwars/vehicles",tags=["Star Wars API"])
async def starwars_vehicles(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    format: str = Query("json")
):
    """Get Star Wars vehicles with pagination and optional search."""
    return await get_vehicles(skip, limit, search, format)

@app.get("/starwars/vehicles/{vehicle_id}",tags=["Star Wars API"])
async def starwars_vehicle_by_id(
    vehicle_id: int,
    format: str = Query("json")
):
    """Get a specific Star Wars vehicle by ID."""
    return await get_vehicle_by_id(vehicle_id, format)