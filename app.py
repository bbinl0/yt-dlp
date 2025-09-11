import os
import logging
from flask import Flask, jsonify, request, render_template, send_file, abort
from werkzeug.middleware.proxy_fix import ProxyFix
from youtube_service import YouTubeService
from urllib.parse import urlparse
import tempfile
import threading
import time

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def create_app():
    app = Flask(__name__, template_folder='templates')
    app.secret_key = os.environ.get("SESSION_SECRET", "youtube-downloader-secret-key")
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    # Initialize YouTube service
    app.youtube_service = YouTubeService()
    return app

app = create_app()
youtube_service = app.youtube_service


@app.route('/')
def index():
    """API usage instructions"""
    return jsonify({
        "message": "Welcome to the YouTube Video Info API!",
        "usage": {
            "/api/video-info": "Get video information. Requires 'url' parameter."
        }
    })

@app.route('/api/video-info')
def get_video_info():
    """Get detailed video information including available formats"""
    try:
        url = request.args.get('url')
        if not url:
            return jsonify({
                'error': 'Missing required parameter: url',
                'success': False
            }), 400
        
        url = url.strip()
        
        # Validate URL
        if not youtube_service.is_valid_youtube_url(url):
            return jsonify({
                'error': 'Invalid YouTube URL',
                'success': False
            }), 400
        
        # Get video information
        video_info = youtube_service.get_video_info(url)
        
        return jsonify({
            'success': True,
            'data': video_info
        })
        
    except Exception as e:
        logging.error(f"Error getting video info: {e}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'YouTube Video Info API',
        'version': '1.0.0'
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found',
        'success': False
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'success': False
    }), 500

from serverless_wsgi import handle_request

def handler(event, context):
    return handle_request(app, event, context)

if __name__ == '__main__':
    app.run(debug=True)