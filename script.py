from flask import Flask, request, send_from_directory
from flask_cors import CORS
from bs4 import BeautifulSoup
import os

app = Flask(__name__)
CORS(app)  # This allows all domains; you can limit it to specific ones for security

# Define a folder to store your cleaned HTML files
STATIC_FOLDER = os.path.join(os.getcwd(), 'static')
os.makedirs(STATIC_FOLDER, exist_ok=True)


@app.route('/upload', methods=['POST'])
def upload_content():
    data = request.get_json()
    filename = data['filename']
    content = data['content']

    if filename.endswith('.html'):
        modified_html = inject_player(content)
        filename_demo = filename.replace('.html', '-demo.html')
        with open(os.path.join(STATIC_FOLDER, filename_demo), 'w', encoding='utf-8') as f:
            f.write(modified_html)
        file_url = f"/static/{filename_demo}"
        return {"status": "success", "message": "File processed successfully.", "file_url": file_url}, 200

    return {"status": "error", "message": "Invalid file type. Please upload an HTML file."}, 400


@app.route('/static/<filename>', methods=['GET'])
def serve_file(filename):
    return send_from_directory(STATIC_FOLDER, filename)


def inject_player(html_content):
    """
    Function to inject a new player container in place of the existing <div class="trv-player-container">.
    """

    soup = BeautifulSoup(html_content, 'html.parser')

    existing_div = soup.find("div", class_="trv-player-container")

    if existing_div:
        parent = existing_div.find_parent()

        if parent:
            script = soup.new_tag('script', **{
                'data-cfasync': 'false',
                'async': True,
                'type': 'text/javascript',
                'src': 'https://go.trvdp.com/init/14013.js?pid=11012'
            })

            player_container = soup.new_tag('div', **{
                'class': 'trv-player-container'
            })

            player_container.append(script)

            existing_div.insert_after(player_container)

            existing_div.decompose()

            print("Player injected successfully!")

    return str(soup)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 9001))
    app.run(host='0.0.0.0', port=port, debug=False)
