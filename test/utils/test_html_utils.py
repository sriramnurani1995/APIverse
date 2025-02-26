import pytest
from src.utils.html_utils import generate_html_page

def test_generate_html_page_basic():
    """Test if generate_html_page returns a valid HTML structure."""
    title = "Test Page"
    content = "<p>Hello, World!</p>"
    html_output = generate_html_page(title, content)
    assert "<!DOCTYPE html>" in html_output
    assert "<html" in html_output
    assert "<head>" in html_output
    assert "<body>" in html_output
    assert "</html>" in html_output

def test_generate_html_page_title():
    """Test if the function correctly sets the page title."""
    title = "My Custom Page"
    html_output = generate_html_page(title, "")

    assert f"<title>{title}</title>" in html_output

def test_generate_html_page_content():
    """Test if the function correctly inserts content."""
    content = "<h1>Welcome</h1>"
    html_output = generate_html_page("Test", content)

    assert content in html_output  # Content should appear in the generated HTML

def test_generate_html_page_default_styles():
    """Test if default styles are applied."""
    html_output = generate_html_page("Styled Page", "<p>Content</p>")

    assert "body {" in html_output  # Check if default CSS is present
    assert "container {" in html_output
    assert "font-family: 'Arial'" in html_output  # One of the default styles

def test_generate_html_page_custom_styles():
    """Test if custom styles override defaults."""
    custom_styles = {"body": "background-color: black;", "h1": "color: red;"}
    html_output = generate_html_page("Styled Page", "<h1>Heading</h1>", styles=custom_styles)

    assert "body { background-color: black; }" in html_output
    assert "h1 { color: red; }" in html_output  # Custom style applied

# Run tests
if __name__ == "__main__":
    pytest.main()
