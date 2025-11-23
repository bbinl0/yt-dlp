import os
import logging
import re
import yt_dlp
from flask import Flask, jsonify, request
from werkzeug.middleware.proxy_fix import ProxyFix

logging.basicConfig(level=logging.DEBUG)


class YouTubeService:

    def __init__(self):
        logging.info("YouTube service initialized")

    def is_valid_youtube_url(self, url):
        youtube_regex = re.compile(
            r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/'
            r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
        return youtube_regex.match(url) is not None

    def get_video_info(self, url):
        try:
            ydl_opts: dict = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }

            info = None
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
            except Exception as e:
                logging.warning(f"Failed to get video info without cookies: {e}")
                cookies_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cookies.txt')
                if os.path.exists(cookies_file):
                    file_size = os.path.getsize(cookies_file)
                    if file_size > 100:
                        logging.info("Retrying with cookies.txt")
                        ydl_opts['cookiefile'] = cookies_file
                        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                            info = ydl.extract_info(url, download=False)
                    else:
                        raise Exception("cookies.txt is empty. Please add your YouTube cookies.")
                else:
                    raise e

            if not info:
                raise Exception("Failed to extract video information")

            video_info = {
                    'title': info.get('title', 'Unknown'),
                    'channel': info.get('uploader', 'Unknown'),
                    'channel_id': info.get('uploader_id', ''),
                    'duration': info.get('duration', 0),
                    'view_count': info.get('view_count', 0),
                    'like_count': info.get('like_count', 0),
                    'upload_date': info.get('upload_date', ''),
                    'description': info.get('description', ''),
                    'thumbnail': info.get('thumbnail', ''),
                    'webpage_url': info.get('webpage_url', url),
                    'video_id': info.get('id', ''),
                    'formats': {
                        'video': [],
                        'audio': []
                    }
            }

            existing_video_formats = set()

            formats = info.get('formats', [])
            for fmt in formats:
                url = fmt.get('url')
                if not url or 'manifest.googlevideo.com' in url or 'm3u8' in url:
                    continue

                vcodec = fmt.get('vcodec', 'none')
                acodec = fmt.get('acodec', 'none')
                height = fmt.get('height')
                abr = fmt.get('abr')
                ext = fmt.get('ext')

                if vcodec != 'none' and height:
                    if ext == 'webm':
                        continue

                    quality = f"{height}p"
                    ftype = 'video_with_audio' if acodec != 'none' else 'video_only'
                    key = (quality, ftype)

                    if key in existing_video_formats:
                        continue
                    existing_video_formats.add(key)

                    video_info['formats']['video'].append({
                        'format_id': fmt.get('format_id'),
                        'url': url,
                        'ext': ext,
                        'filesize': fmt.get('filesize'),
                        'quality_label': quality,
                        'type': ftype
                    })

                elif vcodec == 'none' and acodec != 'none':
                    audio_ext = 'm4a' if 'm4a' in ext else 'mp3'
                    quality_label = f"{abr}kbps" if abr else 'audio'
                    video_info['formats']['audio'].append({
                        'format_id': fmt.get('format_id'),
                        'url': url,
                        'ext': audio_ext,
                        'filesize': fmt.get('filesize'),
                        'quality_label': quality_label,
                        'type': 'audio_only'
                    })

            def safe_quality_int(label):
                try:
                    return int(label.replace('p',''))
                except:
                    return 0

            def safe_bitrate(label):
                try:
                    return int(label.replace('kbps',''))
                except:
                    return 0

            video_info['formats']['video'].sort(key=lambda x: safe_quality_int(x['quality_label']))
            video_info['formats']['audio'].sort(key=lambda x: safe_bitrate(x['quality_label']))

            return video_info

        except Exception as e:
            logging.error(f"Error extracting video info: {e}")
            raise Exception(f"Failed to extract video information: {str(e)}")


youtube_service = YouTubeService()

def create_app():
    app = Flask(__name__, template_folder='templates')
    app.secret_key = os.environ.get("SESSION_SECRET", "youtube-downloader-secret-key")
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    return app

app = create_app()


@app.route('/')
def index():
    """API usage instructions"""
    return jsonify({
        "message": "Welcome to the YouTube Video Info API!",
        "usage": {
            "/api/info": "Get video information. Requires 'url' parameter."
        }
    })

@app.route('/api/info')
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
        
        if not youtube_service.is_valid_youtube_url(url):
            return jsonify({
                'error': 'Invalid YouTube URL',
                'success': False
            }), 400
        
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


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
