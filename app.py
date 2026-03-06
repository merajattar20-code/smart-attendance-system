import os
import logging
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuring logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app and configure database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
db = SQLAlchemy(app)

# Database model for attendance
class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

# Error handling function
@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f'An error occurred: {e}')
    return jsonify({'error': 'An internal error occurred. Please try again later.'}), 500

@app.route('/attendance', methods=['POST'])
def mark_attendance():
    try:
        student_id = request.json.get('student_id')
        if not student_id:
            logger.warning('No student ID provided')
            return jsonify({'error': 'Student ID is required'}), 400

        new_attendance = Attendance(student_id=student_id)
        db.session.add(new_attendance)
        db.session.commit()
        logger.info(f'Attendance marked for student ID: {student_id}')  
        return jsonify({'success': 'Attendance marked successfully'}), 201
    except Exception as e:
        return handle_exception(e)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
