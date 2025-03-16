import os
import random
import utils.helpers as helpers
from google.cloud import datastore
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone



class model:
    def __init__(self):
        self.client = datastore.Client(project='softwareengproject-450500', namespace="apiverse")#set your project id

    # Get user details
    def get_user(self, email):
        """Fetch a user by email."""
        query = self.client.query(kind='User')
        query.add_filter('email', '=', email)
        users = list(query.fetch())
        return users[0] if users else None
    # Insert user details
    def insert_user(self, name, email, password=None,is_oauth=False):
        """Insert user details into Datastore if not exists."""
        if self.get_user(email):
            return False  # User already exists

        if not is_oauth and  email.endswith("@pdx.edu"):
            return False  # Restrict non-PDX users

        hashed_password = generate_password_hash(password)

        key = self.client.key("User")
        user = datastore.Entity(key)
        user.update({
            'name': name,
            'email': email,
            'password': hashed_password,  # OAuth users have None initially
            'is_oauth': is_oauth
        })
        self.client.put(user)
        return True
    # Verify user
    def verify_user(self, email, password):
        """Verify user login credentials."""
        user = self.get_user(email)
    
        if user and "password" in user:
            if check_password_hash(user["password"], password):
                return user  # Successful authentication
    
        return None  
    
    #  Store API Key in Datastore
    def store_api_key(self, user_email, salt, hashed_api_key, expiration_date):
        """Stores a new API key for the user."""
        key = self.client.key('APIKey')
        entity = datastore.Entity(key)
        entity.update({
            'user_email': user_email,
            'salt': salt,
            'hashed_api_key': hashed_api_key,
            'created_at': datetime.now(timezone.utc),
            'expires_at': expiration_date,
            'revoked': False
        })
        self.client.put(entity)

    # Retrieve API Keys for a User
    def get_user_api_keys(self, user_email):
        """Fetch all active API keys for a user, filtering out revoked keys."""
        query = self.client.query(kind='APIKey')
        query.add_filter('user_email', '=', user_email)
        query.add_filter('revoked', '=', False)  # Only return active keys
        return list(query.fetch())  # Returns a list of API key entities

    # Fix Revoke API Key Method 
    def revoke_api_key(self, user_email, api_key_id):
        """Marks an API key as revoked."""
        try:
            key = self.client.key('APIKey', int(api_key_id))
            entity = self.client.get(key)

            if entity:
                if entity.get('user_email') == user_email:
                    entity['revoked'] = True  # Mark key as revoked
                    self.client.put(entity)  # Save updated entity
                    return True
                else:
                    return False  # API key does not belong to the user
            else:
                return False  # API key not found in Datastore

        except Exception:
            return False  # Revocation failed
    
    # Get all active api keys
    def get_all_active_api_keys(self):
        """Fetch all active API keys for validation."""
        query = self.client.query(kind='APIKey')
        query.add_filter('revoked', '=', False)
        return list(query.fetch())
    def clear_image_mappings(self):
        """Clears existing image mappings in Datastore."""
        query = self.client.query(kind="ImageMapping")
        keys = [entity.key for entity in query.fetch()]
        if keys:
            self.client.delete_multi(keys)
            

    def create_image_mappings(self):
        """Creates image mappings by scanning static directories."""
        self.clear_image_mappings()

        category_dirs = helpers.get_category_directories()

        for category, directory in category_dirs.items():
            if not os.path.exists(directory):
                continue

            for filename in os.listdir(directory):
                if filename.endswith((".jpg", ".png", ".jpeg")):
                    name = os.path.splitext(filename)[0]
                    key = self.client.key("ImageMapping", f"{category}-{name}")
                    entity = datastore.Entity(key)
                    entity.update({
                        "category": category,
                        "name": name,
                        "location": os.path.join(directory, filename)
                    })
                    self.client.put(entity)


    def get_image_path(self, category: str, name: str) -> str:
        """Fetch image path from Datastore. Supports 'random' selection."""
        category_dirs = helpers.get_category_directories()

        if category not in category_dirs:
            return None

        if name == "random":
            query = self.client.query(kind="ImageMapping")
            query.add_filter("category", "=", category)
            images = list(query.fetch())

            if images:
                selected_image = random.choice(images)  
                image_path = os.path.abspath(selected_image["location"])
                return image_path
            else:
                return os.path.abspath(os.path.join(category_dirs[category], "default.jpg"))

        key = self.client.key("ImageMapping", f"{category}-{name}")
        entity = self.client.get(key)

        if entity:
            image_path = os.path.abspath(entity["location"])
            if os.path.exists(image_path):
                return image_path
            else:
                print(f"Mapped Image Not Found: {image_path}")
        return os.path.abspath(os.path.join(category_dirs[category], "default.jpg"))
    
    def store_weather_data(self, date, data):
        """Store weather data for a specific date in Datastore."""
        key = self.client.key('Weather', date)
        entity = datastore.Entity(key)
        entity.update(data)
        self.client.put(entity)

    def get_weather_data(self, date):
        """Retrieve weather data for a specific date."""
        key = self.client.key('Weather', date)
        entity = self.client.get(key)
        return dict(entity) if entity else None

    def get_weather_days_in_month(self, month):
        """Retrieve all stored weather dates for a given month."""
        query = self.client.query(kind='Weather')
        query.add_filter("date", ">=", f"{month}-01")
        query.add_filter("date", "<=", f"{month}-31")
        return [entity["date"] for entity in query.fetch()]

    def clear_weather_month(self, month):
        """Delete all weather data entries for an incomplete month to maintain consistency."""
        query = self.client.query(kind='Weather')
        query.add_filter("date", ">=", f"{month}-01")
        query.add_filter("date", "<=", f"{month}-31")
        keys = [entity.key for entity in query.fetch()]
        if keys:
            self.client.delete_multi(keys)
    def save_course(self, courseId, weightage, components):
        """
        Stores the course details in Google Cloud Datastore.

        :param courseId: Unique course identifier
        :param weightage: Dictionary of weightage for different grading components
        :param components: Dictionary of components count (e.g., numHomeworks, numDiscussions, numExams)
        """
        course_key = self.client.key("Course", courseId)
        course = datastore.Entity(course_key)
        course.update({
            "courseId": courseId,
            "weightage": weightage,
            "components": components
        })
        self.client.put(course)

    
    def get_course(self, courseId):
        """
        Fetches course details from Google Cloud Datastore.

        :param courseId: Unique course identifier
        :return: Course entity if found, else None
        """
        course_key = self.client.key("Course", courseId)
        return self.client.get(course_key)

    
    def save_student(self, courseId, studentId, name, components, weightedPercentages, finalPercentage, finalGrade):
        """
        Stores a student’s grades and calculated weighted percentages in Google Cloud Datastore.

        :param courseId: Course ID student belongs to
        :param studentId: Unique student identifier
        :param name: Student name
        :param components: List of grading components (Homework, Discussions, Exams)
        :param weightedPercentages: Dictionary of weighted percentages per grading category
        :param finalPercentage: Final weighted percentage score
        :param finalGrade: Final letter grade (A, B, C, D, F)
        """
        student_key = self.client.key("Student", f"{courseId}_{studentId}")
        student = datastore.Entity(student_key)
        student.update({
            "courseId": courseId,
            "studentId": studentId,
            "name": name,
            "components": components,
            "weightedPercentages": weightedPercentages,
            "finalPercentage": finalPercentage,
            "finalGrade": finalGrade
        })
        self.client.put(student)

    
    def get_students(self, courseId):
        """
        Fetches all students enrolled in a specific course from Google Cloud Datastore.

        :param courseId: Course ID
        :return: List of student entities
        """
        query = self.client.query(kind="Student")
        query.add_filter("courseId", "=", courseId)
        return list(query.fetch())


    def store_starwars_entity(self, kind, data):
        """Store a Star Wars entity in Datastore."""
        key = self.client.key(kind)
        entity = datastore.Entity(key)
        entity.update(data)
        self.client.put(entity)
        return entity

    def get_starwars_entity(self, kind, entity_id):
        """Get a specific Star Wars entity by ID."""
        key = self.client.key(kind, int(entity_id))
        entity = self.client.get(key)
        return entity

    def get_starwars_entities(self, kind, limit=10, offset=0, search=None):
        """Get multiple Star Wars entities with pagination and search."""
        query = self.client.query(kind=kind)
        
        if search:
            # First try exact match on 'name' field
            query.add_filter("name", "=", search)
            results = list(query.fetch(limit=limit, offset=offset))
            
            # If no results, try approximate match
            if not results:
                all_entities = list(self.client.query(kind=kind).fetch())
                results = []
                
                for entity in all_entities:
                    name = entity.get("name", entity.get("title", ""))
                    if search.lower() in name.lower():
                        results.append(entity)
                
                # Apply pagination manually
                total = len(results)
                results = results[offset:offset+limit]
            else:
                # Get total count for pagination info
                total_query = self.client.query(kind=kind)
                total_query.add_filter("name", "=", search)
                total = len(list(total_query.fetch()))
        else:
            # Get total count for pagination info
            total_query = self.client.query(kind=kind)
            total = len(list(total_query.fetch()))
            
            # Get paginated results
            query_iter = query.fetch(limit=limit, offset=offset)
            results = list(query_iter)
        
        return {
            "count": total,
            "results": results
        }

    def import_starwars_data(self, data, kind):
        """Import Star Wars data from JSON."""
        # Clear existing data for this kind
        query = self.client.query(kind=kind)
        keys = [entity.key for entity in query.fetch()]
        if keys:
            self.client.delete_multi(keys)
        
        # Import new data
        for item in data:
            if "fields" in item:
                # Process data from the JSON files
                fields = item["fields"].copy()
                if "pk" in item:
                    fields["id"] = item["pk"]
                
                # Process transport data for vehicles and starships
                if kind in ["Starship", "Vehicle"] and "transport_id" in fields:
                    transport_id = fields["transport_id"]
                    transport_key = self.client.key("Transport", int(transport_id))
                    transport = self.client.get(transport_key)
                    if transport:
                        # Merge transport data with vehicle/starship data
                        for key, value in transport.items():
                            if key not in fields and key != "id":
                                fields[key] = value
                
                # Create entity with specified ID
                if "id" in fields:
                    entity_id = fields.pop("id")
                    key = self.client.key(kind, int(entity_id))
                    entity = datastore.Entity(key=key)
                    entity.update(fields)
                    self.client.put(entity)
                else:
                    self.store_starwars_entity(kind, fields)