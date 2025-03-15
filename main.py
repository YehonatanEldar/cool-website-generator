import asyncio
import nest_asyncio
from google import genai
import json
from flask import Flask, request, redirect, url_for, send_from_directory

# Apply the nest_asyncio patch
nest_asyncio.apply()

# Load API key from JSON
with open('api_key.json', 'r') as file:
    data = json.load(file)

app = Flask(__name__)

# Store generated website code globally
website_code = ''

download_button = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Download HTML</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            margin: 0;
            padding: 0;
            min-height: 100vh;
            background-color: #f5f5f5;
            display: flex;
            flex-direction: column;
        }

        .button-container {
            width: 100%;
            display: flex;
            justify-content: center;
            padding: 20px 0;
            margin-top: auto;
        }

        .download-button {
            padding: 12px 24px;
            background: linear-gradient(135deg, #4a90e2, #3742fa);
            color: white;
            border: none;
            border-radius: 50px;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            outline: none;
            font-weight: bold;
            letter-spacing: 0.5px;
        }

        .download-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
            background: linear-gradient(135deg, #3742fa, #4a90e2);
        }

        .download-button:active {
            transform: translateY(0px);
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .download-icon {
            margin-left: 8px;
        }
    </style>
</head>
<body>
    <div class="button-container">
        <button class="download-button" onclick="downloadHTML()">
            Download HTML <span class="download-icon">⬇️</span>
        </button>
    </div>

    <script>
        function downloadHTML() {
            // Get the current HTML content
            let htmlContent = document.documentElement.outerHTML;
            
            // Create a new HTML document without the button
            const parser = new DOMParser();
            const doc = parser.parseFromString(htmlContent, 'text/html');
            
            // Remove the button container
            const buttonContainer = doc.querySelector('.button-container');
            if (buttonContainer) buttonContainer.remove();
            
            // Remove the script that contains this function
            const scripts = doc.querySelectorAll('script');
            scripts.forEach(script => {
                if (script.textContent.includes('downloadHTML')) {
                    script.remove();
                }
            });
            
            // Get the modified HTML content
            const modifiedHTML = doc.documentElement.outerHTML;
            
            // Create a blob with the modified HTML content
            const blob = new Blob([modifiedHTML], { type: 'text/html' });
            
            // Create a temporary link to download the file
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = 'webpage.html';
            
            // Trigger the download
            document.body.appendChild(link);
            link.click();
            
            // Clean up
            document.body.removeChild(link);
        }
    </script>
</body>
</html>
'''


# Function to generate content using GenAI
# Function to generate content using GenAI
def generate(text):
    client = genai.Client(api_key=data["api_key"])

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=text
        )
        # Extract the text from the response
        if hasattr(response, "text"):
            return response.text
        elif hasattr(response, "candidates") and response.candidates:
            return response.candidates[0].content.parts[0].text
        else:
            return "<h1>Error: Could not extract text from response.</h1>"
    except Exception as e:
        print(f"Error generating content: {e}")
        return f"<h1>Error: Could not generate website.</h1><p>{str(e)}</p>"


# Route to display the generated website
@app.route('/cool_ass_website')
def cool_ass_website():

    if '</body>' in website_code:
        clean_html =  website_code.replace('</body>', download_button + '</body>')
    else:
        clean_html = website_code + download_button

    return clean_html[7:-4].strip()


@app.route('/process', methods=['POST'])
def process_text():
    global website_code
    data = request.get_json()
    input_text = data.get('text', '')
    print(input_text)

    # Generate the website code using the input text
    website_code = generate(
        f"""
        Generate HTML code for a website following this description:
        - If not provided, don't use images.
        - Do not provide an explanation after, just the HTML code.
        - Make it pretty with Javascript.
        {input_text}
        """
    )
    return redirect(url_for('cool_ass_website'))


# Route to display the home page
@app.route('/')
def home():
    # Serve the frontend HTML
    return send_from_directory('', 'index.html')


if __name__ == '__main__':
    # Run Flask app
    app.run(debug=True)
