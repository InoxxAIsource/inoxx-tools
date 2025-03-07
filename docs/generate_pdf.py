"""
PDF Documentation Generator for Inoxx IDE
Converts markdown documentation to styled PDF
"""
import markdown
from weasyprint import HTML, CSS
from pathlib import Path

def generate_pdf():
    # Read markdown content
    with open('docs/DOCUMENTATION.md', 'r', encoding='utf-8') as f:
        markdown_content = f.read()

    # Convert markdown to HTML
    html_content = markdown.markdown(
        markdown_content,
        extensions=['tables', 'fenced_code', 'codehilite', 'toc']
    )

    # Add CSS styling
    css_content = '''
        body {
            font-family: 'Arial', sans-serif;
            line-height: 1.6;
            margin: 40px;
            color: #333;
        }
        h1 { 
            color: #2a5298; 
            font-size: 28px;
            border-bottom: 2px solid #2a5298;
            padding-bottom: 10px;
        }
        h2 { 
            color: #333; 
            font-size: 24px;
            border-bottom: 1px solid #ddd; 
            margin-top: 30px;
        }
        h3 {
            color: #444;
            font-size: 20px;
            margin-top: 25px;
        }
        code { 
            background: #f5f5f5; 
            padding: 2px 4px; 
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
        }
        pre { 
            background: #f5f5f5; 
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #2a5298;
            overflow-x: auto;
        }
        table { 
            border-collapse: collapse; 
            width: 100%;
            margin: 20px 0;
        }
        th, td { 
            border: 1px solid #ddd; 
            padding: 12px; 
            text-align: left;
        }
        th { 
            background-color: #f5f5f5;
            font-weight: bold;
        }
        img {
            max-width: 100%;
            height: auto;
            margin: 20px 0;
        }
        .mermaid {
            margin: 30px 0;
            text-align: center;
        }
        blockquote {
            border-left: 4px solid #2a5298;
            margin: 20px 0;
            padding: 10px 20px;
            background: #f9f9f9;
            color: #666;
        }
        hr {
            border: none;
            border-top: 1px solid #ddd;
            margin: 30px 0;
        }
    '''

    # Create output directory if it doesn't exist
    Path('docs/output').mkdir(exist_ok=True)

    # Generate PDF with enhanced styling
    HTML(string=f'''
        <html>
            <head>
                <style>{css_content}</style>
            </head>
            <body>{html_content}</body>
        </html>
    ''').write_pdf('docs/output/inoxx_documentation.pdf')

if __name__ == '__main__':
    generate_pdf()