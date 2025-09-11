import logging
import yt_dlp
import re


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
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

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

                # Track (quality_label + type) combinations already added
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