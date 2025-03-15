from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from model.model_datastore import model
from utils.caching import cache_response
from utils.html_utils import generate_html_page, generate_download_page
from utils.file_utils import save_file
from typing import Optional
import json
import random
import os

db = model()  # Datastore Model

# Helper function to generate random data for missing fields
def generate_random_data(entity_type, field_name):
    """Generate random data for missing or unknown fields."""
    if field_name == "cost_in_credits":
        return str(random.randint(1000, 10000000))
    elif field_name == "length":
        return str(round(random.uniform(10, 2000), 1))
    elif field_name == "crew":
        return str(random.randint(1, 1000))
    elif field_name == "passengers":
        return str(random.randint(0, 500))
    elif field_name == "cargo_capacity":
        return str(random.randint(100, 100000))
    elif field_name == "hyperdrive_rating":
        return str(round(random.uniform(0.5, 6.0), 1))
    elif field_name == "MGLT":
        return str(random.randint(10, 120))
    elif field_name == "max_atmosphering_speed":
        return str(random.randint(10, 1500))
    elif field_name == "consumables":
        periods = ["days", "weeks", "months", "years"]
        return f"{random.randint(1, 10)} {random.choice(periods)}"
    elif field_name == "population":
        return str(random.randint(1000, 1000000000))
    elif field_name == "diameter":
        return str(random.randint(1000, 20000))
    elif field_name == "rotation_period":
        return str(random.randint(10, 90))
    elif field_name == "orbital_period":
        return str(random.randint(100, 2000))
    elif field_name == "gravity":
        return f"{round(random.uniform(0.5, 2.0), 1)} standard"
    elif field_name == "climate":
        climates = ["temperate", "arid", "tropical", "frozen", "hot", "frigid"]
        return random.choice(climates)
    elif field_name == "terrain":
        terrains = ["mountains", "desert", "grasslands", "forests", "oceans", "swamps", "urban"]
        return ", ".join(random.sample(terrains, random.randint(1, 3)))
    elif field_name == "surface_water":
        return str(random.randint(0, 100))
    elif field_name == "height":
        return str(random.randint(60, 250))
    elif field_name == "mass":
        return str(random.randint(20, 200))
    elif field_name == "hair_color":
        colors = ["black", "brown", "blonde", "red", "white", "none"]
        return random.choice(colors)
    elif field_name == "skin_color":
        colors = ["fair", "light", "dark", "green", "blue", "grey"]
        return random.choice(colors)
    elif field_name == "eye_color":
        colors = ["blue", "brown", "green", "yellow", "red", "orange"]
        return random.choice(colors)
    elif field_name == "birth_year":
        return f"{random.randint(10, 100)}BBY"
    elif field_name == "gender":
        genders = ["male", "female", "n/a", "hermaphrodite"]
        return random.choice(genders)
    # Add more field generators as needed
    return "unknown"

# Generic function to get entities of any type
async def get_entities(kind, skip=0, limit=10, search=None, format="json"):
    """Generic function to get Star Wars entities with pagination."""
    cache_key = f"starwars:{kind}:{skip}:{limit}:{search}:{format}"
    cached_data = cache_response.get(cache_key)
    
    if cached_data:
        if format == "json":
            return JSONResponse(content=cached_data)
        elif format in ["html", "download"]:
            return generate_entity_html_response(cached_data, kind, format)
    
    results = db.get_starwars_entities(kind, limit, skip, search)
    
    # Process results to fill in any missing data
    for entity in results["results"]:
        for key, value in list(entity.items()):
            if value in ["unknown", "n/a", ""]:
                entity[key] = generate_random_data(kind, key)
    
    cache_response.set(cache_key, results, expire=3600)
    
    if format == "json":
        return JSONResponse(content=results)
    elif format in ["html", "download"]:
        return generate_entity_html_response(results, kind, format)

# Generic function to get a single entity by ID
async def get_entity_by_id(kind, entity_id, format="json"):
    """Generic function to get a specific Star Wars entity by ID."""
    cache_key = f"starwars:{kind}:{entity_id}:{format}"
    cached_data = cache_response.get(cache_key)
    
    if cached_data:
        if format == "json":
            return JSONResponse(content=cached_data)
        elif format in ["html", "download"]:
            return generate_entity_detail_html_response(cached_data, kind, format)
    
    entity = db.get_starwars_entity(kind, entity_id)
    
    if not entity:
        raise HTTPException(status_code=404, detail=f"{kind} with ID {entity_id} not found")
    
    # Process entity to fill in any missing data
    for key, value in list(entity.items()):
        if value in ["unknown", "n/a", ""]:
            entity[key] = generate_random_data(kind, key)
    
    cache_response.set(cache_key, entity, expire=3600)
    
    if format == "json":
        return JSONResponse(content=entity)
    elif format in ["html", "download"]:
        return generate_entity_detail_html_response(entity, kind, format)

# Specific entity type functions
async def get_films(skip=0, limit=10, search=None, format="json"):
    return await get_entities("Film", skip, limit, search, format)

async def get_film_by_id(film_id, format="json"):
    return await get_entity_by_id("Film", film_id, format)

async def get_people(skip=0, limit=10, search=None, format="json"):
    return await get_entities("Person", skip, limit, search, format)

async def get_person_by_id(person_id, format="json"):
    return await get_entity_by_id("Person", person_id, format)

async def get_planets(skip=0, limit=10, search=None, format="json"):
    return await get_entities("Planet", skip, limit, search, format)

async def get_planet_by_id(planet_id, format="json"):
    return await get_entity_by_id("Planet", planet_id, format)

async def get_species(skip=0, limit=10, search=None, format="json"):
    return await get_entities("Species", skip, limit, search, format)

async def get_species_by_id(species_id, format="json"):
    return await get_entity_by_id("Species", species_id, format)

async def get_starships(skip=0, limit=10, search=None, format="json"):
    return await get_entities("Starship", skip, limit, search, format)

async def get_starship_by_id(starship_id, format="json"):
    return await get_entity_by_id("Starship", starship_id, format)

async def get_vehicles(skip=0, limit=10, search=None, format="json"):
    return await get_entities("Vehicle", skip, limit, search, format)

async def get_vehicle_by_id(vehicle_id, format="json"):
    return await get_entity_by_id("Vehicle", vehicle_id, format)

# HTML generation for entity lists
def generate_entity_html_response(data, kind, format):
    """Generate HTML or downloadable HTML for entity lists."""
    title = f"Star Wars {kind}s"
    
    # Create a table of entity data
    table_content = "<table><tr>"
    # Add table headers based on the first entity's keys
    if data["results"]:
        first_entity = data["results"][0]
        for key in first_entity:
            if key not in ["pilots", "created", "edited"]:  # Skip some fields
                table_content += f"<th>{key}</th>"
        table_content += "</tr>"
        
        # Add rows for each entity
        for entity in data["results"]:
            table_content += "<tr>"
            for key, value in entity.items():
                if key not in ["pilots", "created", "edited"]:
                    table_content += f"<td>{value}</td>"
            table_content += "</tr>"
    
    table_content += "</table>"
    
    styles = {
        "table": "width: 100%; border-collapse: collapse;",
        "th, td": "border: 1px solid black; padding: 8px; text-align: left;",
        "th": "background-color: #8B0000; color: white; font-weight: bold;",
    }
    
    html_content = generate_html_page(title, table_content, styles=styles)
    
    if format == "html":
        return HTMLResponse(content=html_content)
    
    elif format == "download":
        file_path = save_file(content=html_content, file_extension="html", folder="static/downloads")
        return HTMLResponse(content=generate_download_page(
            f"Your {title} Data", file_path, f"starwars_{kind.lower()}.html", styles))

# HTML generation for entity details
def generate_entity_detail_html_response(entity, kind, format):
    """Generate HTML or downloadable HTML for a single entity."""
    title = f"Star Wars {kind}: {entity.get('name', entity.get('title', 'Details'))}"
    
    # Create a details table
    detail_content = "<table>"
    for key, value in entity.items():
        if key not in ["pilots", "created", "edited"]:  # Skip some fields
            detail_content += f"<tr><th>{key}</th><td>{value}</td></tr>"
    detail_content += "</table>"
    
    styles = {
        "table": "width: 100%; border-collapse: collapse;",
        "th, td": "border: 1px solid black; padding: 8px; text-align: left;",
        "th": "background-color: #8B0000; color: white; font-weight: bold; width: 30%;",
    }
    
    html_content = generate_html_page(title, detail_content, styles=styles)
    
    if format == "html":
        return HTMLResponse(content=html_content)
    
    elif format == "download":
        entity_name = entity.get('name', entity.get('title', 'entity')).lower().replace(' ', '_')
        file_path = save_file(content=html_content, file_extension="html", folder="static/downloads")
        return HTMLResponse(content=generate_download_page(
            f"Your {title} Data", file_path, f"starwars_{kind.lower()}_{entity_name}.html", styles))

# Function to import Star Wars data
def import_all_starwars_data():
    """Import all Star Wars data from JSON files."""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    
    # Import films
    with open(os.path.join(data_dir, 'films.json'), 'r') as f:
        films = json.load(f)
        db.import_starwars_data(films, "Film")
    
    # Import people
    with open(os.path.join(data_dir, 'people.json'), 'r') as f:
        people = json.load(f)
        db.import_starwars_data(people, "Person")
    
    # Import planets
    with open(os.path.join(data_dir, 'planets.json'), 'r') as f:
        planets = json.load(f)
        db.import_starwars_data(planets, "Planet")
    
    # Import species
    with open(os.path.join(data_dir, 'species.json'), 'r') as f:
        species = json.load(f)
        db.import_starwars_data(species, "Species")
    
    # First import transport data
    with open(os.path.join(data_dir, 'transport.json'), 'r') as f:
        transports = json.load(f)
        db.import_starwars_data(transports, "Transport")
    
    # Import starships with reference to transport
    with open(os.path.join(data_dir, 'starships.json'), 'r') as f:
        starships = json.load(f)
        for starship in starships:
            if "fields" in starship:
                starship["fields"]["transport_id"] = starship["pk"]
        db.import_starwars_data(starships, "Starship")
    
    # Import vehicles with reference to transport
    with open(os.path.join(data_dir, 'vehicles.json'), 'r') as f:
        vehicles = json.load(f)
        for vehicle in vehicles:
            if "fields" in vehicle:
                vehicle["fields"]["transport_id"] = vehicle["pk"]
        db.import_starwars_data(vehicles, "Vehicle")
    
    print("Successfully imported all Star Wars data!")

def check_starwars_data_exists():
    """Check if Star Wars data is already in the database.
    Returns True if data exists, False otherwise."""
    
    # Check if there's at least some Film data
    film_data = db.get_starwars_entities("Film", limit=1)
    if film_data["count"] > 0:
        return True
    
    # Check if there's at least some Person data
    person_data = db.get_starwars_entities("Person", limit=1)
    if person_data["count"] > 0:
        return True
    
    # No data found
    return False