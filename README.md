### YouTube Video Info API

This is a synchronous Flask API designed to fetch and provide detailed information about YouTube videos, including video and audio download links in various formats. The API is built to be easily deployable on a platform like Railway using a Gunicorn server.

-----

### Features

  * **Video Information**: Retrieve essential video details such as title, channel, duration, view count, and thumbnail.
  * **Format Listing**: Get a list of available video and audio formats, including direct download links.
  * **CORS Enabled**: The API is configured to handle cross-origin requests, allowing it to be used by any frontend application.
  * **Cookie Support**: Can use a `cookies.txt` file to access private, age-restricted, or authenticated content.
  * **Serverless-Compatible Design**: The core logic is structured to be run in a serverless environment, although a containerized approach is recommended for this specific use case.

-----

### Project Structure

```
your-flask-project/
├── wsgi.py              # Main Flask application and API routes
├── youtube_service.py   # Core logic for fetching YouTube video info
├── requirements.txt     # Python dependencies
├── Procfile             # Command for the web server (Gunicorn)
└── cookies.txt          # (Optional) File for storing YouTube cookies
```

-----

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/your-flask-project.git
    cd your-flask-project
    ```
2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

-----

### API Endpoints

#### 1\. Base URL

  * **Endpoint**: `/`
  * **Method**: `GET`
  * **Description**: A simple welcome message and usage instructions.
  * **Response**:
    ```json
    {
      "message": "Welcome to the YouTube Video Info API!",
      "usage": "Use the /video-info endpoint to get video details.",
      "example": "https://your-api-url.com/video-info?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    }
    ```

#### 2\. Video Info

  * **Endpoint**: `/video-info`
  * **Method**: `GET`
  * **Description**: Fetches detailed information for a given YouTube video URL.
  * **Parameters**:
      * `url` (query parameter): The URL of the YouTube video.
  * **Example Request**:
    ```
    https://your-api-url.com/video-info?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ
    ```
  * **Response**:
    ```json
    {
      "data": {
        "title": "...",
        "channel": "...",
        "duration": "...",
        "formats": {
          "video": [
            {
              "quality_label": "1080p",
              "ext": "mp4",
              "url": "..."
            }
          ],
          "audio": [
            {
              "quality_label": "128kbps",
              "ext": "m4a",
              "url": "..."
            }
          ]
        }
      }
    }
    ```
  * **Error Responses**:
      * `400 Bad Request`: If the `url` parameter is missing or invalid.
      * `500 Internal Server Error`: If `yt-dlp` fails to retrieve video information.

-----

### Deployment on Railway

This project is configured for deployment on Railway using a **Procfile** and **Gunicorn**.

1.  **Push your code to a GitHub repository.**
2.  **Create a new project on Railway.**
3.  **Link your GitHub repository** to the new project.
4.  **Railway will automatically detect the `requirements.txt` and `Procfile`** and deploy your application. The `gunicorn` server will handle your Flask API.
