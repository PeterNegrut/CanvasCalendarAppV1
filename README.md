# Canvas Calendar API

A Flask-based API that generates iCalendar files from Canvas assignments.

## Features

- Fetches assignments from Canvas API
- Generates iCalendar (.ics) files
- Provides JSON API endpoints for assignments
- Health check endpoint

## API Endpoints

- `GET /api/health` - Health check endpoint
- `GET /api/calendar` - Generate and download calendar file
- `GET /api/assignments` - Get assignments as JSON

## Local Development

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file with your Canvas credentials:
   ```
   CANVAS_API_TOKEN=your_token_here
   CANVAS_URL=your_canvas_url_here
   ```
5. Run the development server:
   ```bash
   python app.py
   ```

## Deployment to Render

1. Create a Render account if you don't have one
2. Connect your GitHub repository to Render
3. Create a new Web Service
4. Configure the following environment variables in Render:
   - `CANVAS_API_TOKEN`
   - `CANVAS_URL`
5. Deploy!

## Mobile App Integration

To integrate with a mobile app:

1. Use the `/api/assignments` endpoint to fetch assignments as JSON
2. Use the `/api/calendar` endpoint to download the calendar file
3. Implement calendar import functionality in your mobile app

## Security Notes

- Never commit your `.env` file or expose your Canvas API token
- Use HTTPS in production
- Consider implementing authentication for the API endpoints
