import logging
from flask import Flask, request
from flask_restful import Resource, Api
from werkzeug.exceptions import BadRequest
from flask_cors import CORS
from youtube_service import YouTubeService

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize the Flask app and API
app = Flask(__name__)
# Add CORS to the app
CORS(app)
api = Api(app)
youtube_service = YouTubeService()

# --- New Route for Base URL ---
@app.route('/')
def home():
    """
    Handles requests to the base URL and provides API usage instructions.
    """
    return {
        "message": "Welcome to the YouTube Video Info API!",
        "usage": "Use the /video-info endpoint to get video details.",
        "example": "https://your-api-url.com/video-info?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    }

# --- VideoInfo API Resource ---
class VideoInfo(Resource):
    """
    API resource to get YouTube video information.
    """
    def get(self):
        """
        Handles GET requests to retrieve video information.
        """
        url = request.args.get('url')
        if not url:
            raise BadRequest("Missing 'url' query parameter.")
        
        if not youtube_service.is_valid_youtube_url(url):
            return {"error": "Invalid YouTube URL provided."}, 400

        try:
            video_info = youtube_service.get_video_info(url)
            return {"data": video_info}, 200
        except Exception as e:
            logging.error(f"API Error processing request for URL {url}: {e}")
            return {"error": str(e)}, 500

# Add the resource to the API
api.add_resource(VideoInfo, '/video-info')

# Main entry point for local development
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
