from model.model_datastore import model
from utils.grade_utils import validate_weightage, generate_marks,calculate_weighted_percentage
from faker import Faker

fake = Faker()

db = model()


def create_course(courseId, numStudents, numHomeworks, numDiscussions, numExams, homeworkWeight, discussionWeight, examWeight):
    """Creates a course and generates random student data with grades using grade_utils."""

   
    validate_weightage(homeworkWeight, discussionWeight, examWeight)

    
    db.save_course(courseId, 
        weightage={"Homework": homeworkWeight, "Discussions": discussionWeight, "FinalExam": examWeight},
        components={"Homework": numHomeworks, "Discussions": numDiscussions, "FinalExam": numExams}
    )

   
    for studentId in range(1, numStudents + 1):
        student_name = fake.name()
        components = []

        
        for category, num_items, weight in [
            ("Homework", numHomeworks, homeworkWeight), 
            ("Discussions", numDiscussions, discussionWeight), 
            ("FinalExam", numExams, examWeight)
        ]:
            for i in range(1, num_items + 1):
                score = generate_marks()  
                components.append({"type": category, "component": f"{category} {i}", "marks": score, "totalMarks": 100})


        weighted_percentages, final_percentage, final_grade = calculate_weighted_percentage(components, {
            "Homework": homeworkWeight,
            "Discussions": discussionWeight,
            "FinalExam": examWeight
        })

        db.save_student(courseId, studentId, student_name, components, weighted_percentages, final_percentage, final_grade)

    return {"message": "Course and students generated successfully", "courseId": courseId}


def get_course_header(courseId):
    return db.get_course(courseId)

def get_students_by_course(courseId):
    return db.get_students(courseId)
