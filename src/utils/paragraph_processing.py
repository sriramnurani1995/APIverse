import random
from utils.file_utils import save_file
from utils.html_utils import generate_html_page
from google.cloud import aiplatform_v1beta1 as aiplatform  # Use Gemini-compatible API
import vertexai
from vertexai.generative_models import GenerativeModel

# Vertex AI Configuration
PROJECT_ID = "cloud-varun-varunch"
LOCATION = "us-central1"  # Update based on your region
MODEL_NAME = "gemini-1.5-flash-002"  # Using Gemini model

def generate_paragraphs(type_param: str, length: str, count: int, topic=None, tone=None):
    """Generates paragraphs using predefined text (manual) or Gemini AI (llm)."""
    
    # AI-based Generation (Google Vertex AI)
    if type_param == "llm":
        return [generate_llm_paragraph(topic, tone, length) for _ in range(count)]
    
    # Manual generation (Predefined Text)
    return generate_manual_paragraphs(type_param, length, count)
def generate_manual_paragraphs(type: str, length: str, count: int):
    """Generates randomized placeholder paragraphs based on type, length, and count."""
    
    text_library = {
        "lorem": [
            "Lorem ipsum dolor sit amet", "consectetur adipiscing elit", 
            "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua",
            "Ut enim ad minim veniam", "quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat",
            "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur"
        ],
        "business": [
            "Synergize core competencies", "Leverage key deliverables", 
            "Drive innovation", "Scale vertical markets", "Engage stakeholders", 
            "Optimize operational efficiencies", "Empower team collaboration", 
            "Maximize ROI", "Pivot strategy", "Disrupt traditional paradigms"
        ],
        "tech": [
            "Implement RESTful APIs", "Build scalable microservices", 
            "Leverage cloud computing", "Optimize for mobile-first design", 
            "Integrate CI/CD pipelines", "Deploy on Kubernetes", "Debug production issues",
            "Write efficient algorithms", "Scale distributed systems", "Embrace open-source software"
        ],
        "hipster": [
            "Sip artisanal coffee", "Ride a fixie bike", "Wear vintage flannel",
            "Shop at farmers markets", "Brew craft beer", "Grow an urban garden",
            "Listen to indie vinyls", "Use a typewriter", "Attend pop-up galleries",
            "Advocate for slow food", "Explore hidden speakeasies", "Buy fair-trade avocado toast"
        ],
        "cats": [
            "Rub against legs", "Knock over a plant", "Play with dangling string",
            "Chase laser dot", "Sleep in cardboard box", "Bring dead mouse as a gift",
            "Attack invisible prey", "Hide under the bed", "Stare at the wall for no reason",
            "Purr meow", "Drink water from the faucet"
        ],
        "pup": [
            "Bark at the mailman", "Chase squirrels", "Play fetch",
            "Wag tail", "Dig holes", "Sniff hydrants", "Chew on bones",
            "Roll in the grass", "Pant happily", "Jump in puddles",
            "Beg for treats", "Run in circles", "Howl at sirens"
        ]
    }
    
    word_counts = {"short": 40, "medium": 100, "long": 200}
    word_count = word_counts.get(length, word_counts["medium"])
    library = text_library.get(type, text_library["lorem"])

    paragraphs = []
    
    for _ in range(count):
        random.shuffle(library)  # Randomize order of phrases
        paragraph = []
        word_counter = 0
        sentence = ""

        while word_counter < word_count:
            phrase = random.choice(library)  # Pick a random phrase
            word_count_in_phrase = len(phrase.split())

            if word_counter + word_count_in_phrase > word_count:
                break

            sentence += " " + phrase if sentence else phrase
            word_counter += word_count_in_phrase

            # Randomly break sentence after 8-12 words
            if word_counter >= 8 and random.random() > 0.5:
                sentence = sentence.capitalize() + "."
                paragraph.append(sentence)
                sentence = ""

        if sentence:
            paragraph.append(sentence.capitalize() + ".")

        paragraphs.append(" ".join(paragraph))

    return paragraphs


def generate_llm_paragraph(topic, tone, length):
    """Generates a paragraph using Google Vertex AI's Gemini model."""
    try:
        # Load Gemini model
        model = GenerativeModel("gemini-1.5-flash-002")

        # Construct dynamic prompt for better AI generation
        prompt = (
            f"Generate a {tone} paragraph about {topic}. The paragraph should be {length} in length.\n"
            "Ensure the content is engaging, well-structured, and follows a coherent flow."
        )

        # Define generation configuration
        generation_config = {
            "max_output_tokens": 300,
            "temperature": 0.7,
            "top_p": 0.8
        }

        # Generate content using Gemini
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )

        # Extract and return generated text
        return response.text.strip() if response.text else "Error: No response from Gemini model."

    except Exception as e:
        return f"Error generating paragraph: {str(e)}"
