import random

def validate_weightage(homeworkWeight, discussionWeight, examWeight):
    """
    Validate that the total weightage sums up to 100%.
    Raises a ValueError if the sum is not exactly 100.
    """
    total_weight = homeworkWeight + discussionWeight + examWeight
    if total_weight != 100:
        raise ValueError(f"Total weightage must be exactly 100%. Provided: {total_weight}%")

def generate_marks(mean=85, stddev=7):
    """
    Generate marks using a normal distribution while ensuring they stay within 0-100%.
    """
    return max(0, min(100, round(random.gauss(mean, stddev))))

def calculate_weighted_percentage(components, weightage):
    """
    Calculates the weighted percentage for each grading category (Homework, Discussions, Exams).
    
    :param components: List of dictionaries containing marks per category
    :param weightage: Dictionary with weightage for each grading category
    :return: Tuple (weighted percentages dictionary, final percentage, final letter grade)
    """
    total_weighted_score = 0
    weighted_percentages = {}

    for category, weight in weightage.items():
        category_scores = [comp['marks'] / comp['totalMarks'] * 100 for comp in components if comp['type'] == category]
        
        if category_scores:
            category_avg = sum(category_scores) / len(category_scores)  # Compute average percentage
            category_weighted = (category_avg * weight) / 100  # Apply weightage
            weighted_percentages[category] = round(category_weighted, 2)
            total_weighted_score += category_weighted
        else:
            weighted_percentages[category] = 0.0  # Default if no scores exist for a category

    # Assign final letter grade based on the final percentage
    final_grade = assign_letter_grade(total_weighted_score)

    return weighted_percentages, round(total_weighted_score, 2), final_grade

def assign_letter_grade(percentage):
    """
    Assigns a letter grade based on percentage.
    
    A: 90-100
    B: 80-89
    C: 70-79
    D: 60-69
    F: Below 60
    """
    if percentage >= 90:
        return "A"
    elif percentage >= 80:
        return "B"
    elif percentage >= 70:
        return "C"
    elif percentage >= 60:
        return "D"
    else:
        return "F"
