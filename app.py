from flask import Flask, jsonify, send_file
from canvas_calendar import CanvasCalendar
import os
from dotenv import load_dotenv

app = Flask(__name__)

# Load environment variables
load_dotenv()

@app.route('/', methods=['GET'])
def root():
    """Root endpoint with API information"""
    return jsonify({
        "name": "Canvas Calendar API",
        "version": "1.0",
        "endpoints": {
            "health": "/api/health - Check API health",
            "assignments": "/api/assignments - Get assignments as JSON",
            "calendar": "/api/calendar - Download calendar file"
        }
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"})

@app.route('/api/calendar', methods=['GET'])
def get_calendar():
    """Generate and return the calendar file"""
    try:
        calendar = CanvasCalendar()
        assignments = calendar.get_assignments()
        
        if not assignments:
            return jsonify({"error": "No assignments found"}), 404
            
        calendar.create_calendar()
        
        # Return the calendar file
        return send_file(
            'canvas_calendar.ics',
            mimetype='text/calendar',
            as_attachment=True,
            download_name='canvas_calendar.ics'
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/assignments', methods=['GET'])
def get_assignments():
    """Get assignments as JSON"""
    try:
        calendar = CanvasCalendar()
        assignments = calendar.get_assignments()
        
        if not assignments:
            return jsonify({"error": "No assignments found"}), 404
            
        # Convert datetime objects to strings for JSON serialization
        assignments_json = []
        for assignment in assignments:
            assignment_copy = assignment.copy()
            assignment_copy['due_date'] = assignment_copy['due_date'].isoformat()
            assignments_json.append(assignment_copy)
            
        return jsonify(assignments_json)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 