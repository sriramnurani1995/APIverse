def generate_html_page(title: str, content: str, styles: dict = None):
    """Generates a simple HTML page with dynamic styles."""
    
 
    default_styles = {
        "body": "font-family: 'Arial', sans-serif; background-color: #f4f4f4; color: #333; margin: 0; padding: 0; display: flex; justify-content: center; align-items: center; min-height: 100vh;",
        "container": "max-width: 900px; margin: auto; padding: 20px; background: white; border-radius: 10px; box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);",
        "h1": "font-size: 30px; color: #222; text-align: center; margin-bottom: 20px; display:block",
        "download-btn": "display: inline-block; padding: 12px 24px; font-size: 18px; font-weight: bold; text-decoration: none; color: white; background: #007BFF; border-radius: 5px; transition: background 0.3s ease-in-out;",
        "download-btn-hover": "background: #0056b3;"
    }

    merged_styles = {**default_styles, **(styles or {})}

    css_styles = "<style>\n"
    for element, css in merged_styles.items():
        css_styles += f"{element} {{ {css} }}\n"  
    css_styles += "</style>"

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        {css_styles}  
    </head>
    <body>
    
    <main>
        <div class="container">
            <h1>{title}</h1>
            {content}  
        </div>
    </main>
    </body>
    </html>
    """



def generate_download_page(api_name: str, file_path: str, download_filename: str, styles: dict = None):
    """Generates a reusable download page with dynamic styles."""
    
    content = f"""
        <p>Click below to download:</p>
        <a href="/download_file?file={file_path}" download="{download_filename}" class="download-btn">
           Download {api_name} File
        </a>
    """
    return generate_html_page(f"Download {api_name} File", content, styles)
