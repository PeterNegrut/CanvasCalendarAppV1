from flask import Flask, jsonify, send_file, render_template, request, redirect, url_for, session
from canvas_calendar import CanvasCalendar
import os
from dotenv import load_dotenv
from flask_cors import CORS
import logging
import requests
from urllib.parse import urlencode

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Canvas OAuth settings
CANVAS_URL = os.getenv('CANVAS_URL', 'https://canvas.ucsd.edu')
CLIENT_ID = os.getenv('CANVAS_CLIENT_ID')
CLIENT_SECRET = os.getenv('CANVAS_CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI', 'https://your-render-url.onrender.com/callback')

# Flask session secret
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here')

def get_auth_url():
    """Generate Canvas OAuth authorization URL"""
    params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'scope': 'url:GET|/api/v1/courses url:GET|/api/v1/courses/:id/assignments'
    }
    return f"{CANVAS_URL}/login/oauth2/auth?{urlencode(params)}"

def get_access_token(code):
    """Exchange authorization code for access token"""
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code'
    }
    response = requests.post(f"{CANVAS_URL}/login/oauth2/token", data=data)
    response.raise_for_status()
    return response.json()['access_token']

@app.route('/', methods=['GET'])
def root():
    """Serve the login page"""
    if 'access_token' not in session:
        return render_template('login.html', auth_url=get_auth_url())
    return render_template('index.html')

@app.route('/callback', methods=['GET'])
def callback():
    """Handle OAuth callback"""
    code = request.args.get('code')
    if not code:
        return redirect(url_for('root'))
    
    try:
        access_token = get_access_token(code)
        session['access_token'] = access_token
        return redirect(url_for('root'))
    except Exception as e:
        logger.error(f"Error in callback: {str(e)}")
        return redirect(url_for('root'))

@app.route('/logout', methods=['GET'])
def logout():
    """Clear the session"""
    session.clear()
    return redirect(url_for('root'))

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"})

@app.route('/api/calendar', methods=['GET'])
def get_calendar():
    """Generate and return the calendar file"""
    if 'access_token' not in session:
        return jsonify({"error": "Not authenticated"}), 401
        
    try:
        logger.info("Starting calendar generation...")
        calendar = CanvasCalendar(session['access_token'])
        assignments = calendar.get_assignments()
        
        if not assignments:
            logger.warning("No assignments found")
            return jsonify({"error": "No assignments found"}), 404
            
        logger.info(f"Found {len(assignments)} assignments")
        calendar.create_calendar()
        
        return send_file(
            'canvas_calendar.ics',
            mimetype='text/calendar',
            as_attachment=True,
            download_name='canvas_calendar.ics'
        )
    except Exception as e:
        logger.error(f"Error generating calendar: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/assignments', methods=['GET'])
def get_assignments():
    """Get assignments as JSON"""
    if 'access_token' not in session:
        return jsonify({"error": "Not authenticated"}), 401
        
    try:
        logger.info("Fetching assignments...")
        calendar = CanvasCalendar(session['access_token'])
        assignments = calendar.get_assignments()
        
        if not assignments:
            logger.warning("No assignments found")
            return jsonify({"error": "No assignments found"}), 404
            
        logger.info(f"Found {len(assignments)} assignments")
        assignments_json = []
        for assignment in assignments:
            assignment_copy = assignment.copy()
            assignment_copy['due_date'] = assignment_copy['due_date'].isoformat()
            assignments_json.append(assignment_copy)
            
        return jsonify(assignments_json)
    except Exception as e:
        logger.error(f"Error fetching assignments: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 