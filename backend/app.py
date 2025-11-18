from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure
from bson import ObjectId
from datetime import datetime, timezone
import os
from flask import send_from_directory
from dotenv import load_dotenv
import atexit
import functools
from agent.agent_core import ElevateUAgent

# Import our intelligent chatbot service
try:
    from agent.agent_core import ElevateUAgent
    chatbot_available = True
except ImportError as e:
    print(f"Chatbot Agent service not available: {e}")
    chatbot_available = False

load_dotenv()

app = Flask(__name__)
CORS(app)

# MongoDB connection with connection pooling and error handling
MONGO_URI = os.getenv('MONGO_URI')
DB_NAME = os.getenv('DB_NAME', 'elevateu')

try:
    # Use connection pooling for better performance
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000,  # 5 second timeout
        connectTimeoutMS=5000,
        maxPoolSize=50,
        minPoolSize=10
    )
    # Test connection
    client.server_info()
    db = client[DB_NAME]
    print(f"Connected to MongoDB: {DB_NAME}")
except (ServerSelectionTimeoutError, ConnectionFailure) as e:
    print(f"MongoDB connection failed: {e}")
    print("Please ensure MongoDB is running or update MONGO_URI in .env")
    client = None
    db = None

# Cleanup on exit
def close_mongodb_connection():
    if client:
        client.close()
        print("MongoDB connection closed")

atexit.register(close_mongodb_connection)

# Collections (with error handling)
def get_collection(name):
    if db is None:
        raise ConnectionError("MongoDB not connected")
    return db[name]

# Initialize collections only if db is connected
if db is not None:
    courses_collection = get_collection('courses')
    users_collection = get_collection('users')
    enrollments_collection = get_collection('enrollments')
    progress_collection = get_collection('progress')
    study_updates_collection = get_collection('study_updates')
    chat_sessions_collection = get_collection('chat_sessions')
else:
    courses_collection = None
    users_collection = None
    enrollments_collection = None
    progress_collection = None
    study_updates_collection = None
    chat_sessions_collection = None

# Initialize the ElevateUAgent only once with proper parameters
agent = None
if chatbot_available and db is not None:
    try:
        agent = ElevateUAgent(
            mongo_db=db,
            api_key=os.getenv("GEMINI_API_KEY")
        )
        print(" * ElevateU Agent initialized successfully")
    except Exception as e:
        print(f" * Failed to initialize ElevateU Agent: {e}")
        agent = None
else:
    print(" * ElevateU Agent not initialized (missing dependencies)")

def safe_progress(progress, course):
    """Ensures progress is always a valid dict structure"""
    if not isinstance(progress, dict):
        progress = {}

    # Ensure course topics is a list
    course_topics = course.get("topics", [])
    if not isinstance(course_topics, list):
        course_topics = []

    return {
        "progress": progress.get("progress", 0),
        "completedTopics": progress.get("completedTopics", []),
        "totalTopics": len(course_topics),
        "topics": course_topics,
    }

def sanitize_topics(topics):
    """Ensure topics is always a list of dicts."""
    if not isinstance(topics, list):
        return []
    clean = []
    for t in topics:
        if isinstance(t, dict):
            clean.append(t)
    return clean

# Helper function to convert ObjectId to string
def serialize_doc(doc):
    if doc and '_id' in doc:
        doc['_id'] = str(doc['_id'])
    return doc

# Helper to check MongoDB connection
def check_mongodb():
    if db is None:
        return jsonify({'error': 'MongoDB not connected. Please check your connection settings.'}), 503
    return None

# Admin authentication middleware
def admin_required():
    """Check if user is admin before allowing access to admin endpoints"""
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            # Simple admin check - in production, use proper authentication
            # For now, check for admin role in database or use a simple admin key
            admin_key = request.headers.get('X-Admin-Key')
            user_id = request.headers.get('X-User-ID')

            # Accept either admin key or admin role
            if admin_key == 'elevateu-admin-2024':
                return f(*args, **kwargs)
            elif user_id:
                user = users_collection.find_one({
                    '$or': [
                        {'clerkId': user_id},
                        {'_id': ObjectId(user_id) if ObjectId.is_valid(user_id) else None}
                    ]
                })
                if user and user.get('role') == 'admin':
                    return f(*args, **kwargs)

            return jsonify({'error': 'Admin access required'}), 403
        return decorated_function
    return decorator

# -------------------------------------------------------
# Serve React Frontend (works in local + Docker)
# -------------------------------------------------------
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    # When running locally, user will run Vite, so skip serving React
    if os.environ.get("FLASK_ENV") == "development":
        return jsonify({"message": "Frontend is served by Vite in local mode"}), 200

    # In Docker/VM production:
    static_folder = os.path.join(app.root_path, "static")

    if path != "" and os.path.exists(os.path.join(static_folder, path)):
        return send_from_directory(static_folder, path)

    # otherwise return index.html
    return send_from_directory(static_folder, "index.html")

# Courses endpoints
@app.route('/api/courses', methods=['GET'])
def get_courses():
    courses = list(courses_collection.find())
    # Add enrollment count for each course
    for course in courses:
        enrollment_count = enrollments_collection.count_documents({'courseId': str(course['_id'])})
        course['enrollmentCount'] = enrollment_count
    return jsonify([serialize_doc(course) for course in courses])

@app.route('/api/courses', methods=['POST'])
def create_course():
    data = request.json
    course = {
        'title': data.get('title'),
        'description': data.get('description'),
        'instructor': data.get('instructor', ''),
        'duration': data.get('duration', ''),
        'topics': data.get('topics', []),
        'createdAt': datetime.now(timezone.utc).isoformat()
    }
    result = courses_collection.insert_one(course)
    course['_id'] = str(result.inserted_id)
    return jsonify(serialize_doc(course)), 201

@app.route('/api/courses/<course_id>', methods=['GET'])
def get_course(course_id):
    course = courses_collection.find_one({'_id': ObjectId(course_id)})
    if not course:
        return jsonify({'error': 'Course not found'}), 404
    return jsonify(serialize_doc(course))

@app.route('/api/courses/<course_id>', methods=['PUT'])
def update_course(course_id):
    data = request.json
    update_data = {
        'title': data.get('title'),
        'description': data.get('description'),
        'instructor': data.get('instructor', ''),
        'duration': data.get('duration', ''),
        'topics': data.get('topics', [])
    }
    result = courses_collection.update_one(
        {'_id': ObjectId(course_id)},
        {'$set': update_data}
    )
    if result.matched_count == 0:
        return jsonify({'error': 'Course not found'}), 404
    course = courses_collection.find_one({'_id': ObjectId(course_id)})
    return jsonify(serialize_doc(course))

@app.route('/api/courses/<course_id>', methods=['DELETE'])
def delete_course(course_id):
    result = courses_collection.delete_one({'_id': ObjectId(course_id)})
    if result.deleted_count == 0:
        return jsonify({'error': 'Course not found'}), 404
    # Also delete enrollments and progress
    enrollments_collection.delete_many({'courseId': course_id})
    progress_collection.delete_many({'courseId': course_id})
    return jsonify({'message': 'Course deleted'}), 200

# User endpoints
@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.json

    # Default role unless admin manually assigned
    role = data.get('role', 'student')

    user = {
        'clerkId': data.get('clerkId'),
        'name': data.get('name'),
        'email': data.get('email'),
        'role': role,
        'createdAt': datetime.now(timezone.utc).isoformat()
    }
    # Check if user already exists by clerkId or email
    existing = users_collection.find_one({
        '$or': [
            {'clerkId': user['clerkId']},
            {'email': user['email']}
        ]
    })
    if existing:
        return jsonify(serialize_doc(existing))
    result = users_collection.insert_one(user)
    user['_id'] = str(result.inserted_id)
    return jsonify(serialize_doc(user)), 201

@app.route('/api/users/<clerk_id>', methods=['GET'])
def get_user(clerk_id):
    user = users_collection.find_one({'clerkId': clerk_id})
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(serialize_doc(user))

@app.route('/api/users/<clerk_id>', methods=['PUT'])
def update_user(clerk_id):
    data = request.json
    user = users_collection.find_one({'clerkId': clerk_id})
    if not user:
        return jsonify({'error': 'User not found'}), 404

    update_data = {}
    if 'role' in data:
        update_data['role'] = data['role']
    if 'name' in data:
        update_data['name'] = data['name']
    if 'email' in data:
        update_data['email'] = data['email']

    result = users_collection.update_one(
        {'clerkId': clerk_id},
        {'$set': update_data}
    )

    if result.modified_count > 0:
        updated_user = users_collection.find_one({'clerkId': clerk_id})
        return jsonify(serialize_doc(updated_user))
    else:
        return jsonify({'message': 'No changes made'}), 200

# Enrollment endpoints
@app.route('/api/enrollments', methods=['POST'])
def create_enrollment():
    data = request.json
    enrollment = {
        'userId': data.get('userId'),
        'courseId': data.get('courseId'),
        'enrolledAt': datetime.now(timezone.utc).isoformat(),
        'status': 'in_progress'
    }
    # Check if already enrolled
    existing = enrollments_collection.find_one({
        'userId': enrollment['userId'],
        'courseId': enrollment['courseId']
    })
    if existing:
        return jsonify(serialize_doc(existing))
    result = enrollments_collection.insert_one(enrollment)
    enrollment['_id'] = str(result.inserted_id)
    # Initialize progress
    course = courses_collection.find_one({'_id': ObjectId(enrollment['courseId'])})
    # Sanitize topics list
    course['topics'] = sanitize_topics(course.get('topics', []))
    if course:
        progress = {
            'userId': enrollment['userId'],
            'courseId': enrollment['courseId'],
            'completedTopics': [],
            'progress': 0,
            'lastUpdated': datetime.now(timezone.utc).isoformat()
        }
        progress_collection.insert_one(progress)
    return jsonify(serialize_doc(enrollment)), 201

@app.route('/api/enrollments/user/<user_id>', methods=['GET'])
def get_user_enrollments(user_id):
    # Try to find user by both user_id and clerk_id
    user = users_collection.find_one({
        '$or': [
            {'clerkId': user_id},
            {'_id': ObjectId(user_id) if ObjectId.is_valid(user_id) else None}
        ]
    })
    
    if user:
        user_id_str = str(user['_id'])
        clerk_id = user.get('clerkId', '')
        # Get enrollments using both student ID and clerk ID
        enrollments = list(enrollments_collection.find({
            '$or': [
                {'userId': user_id_str},
                {'userId': clerk_id},
                {'userId': user_id}
            ]
        }))
    else:
        # Fallback to direct user_id lookup
        enrollments = list(enrollments_collection.find({'userId': user_id}))
    
    # Get course details for each enrollment
    for enrollment in enrollments:
        try:
            course = courses_collection.find_one({'_id': ObjectId(enrollment['courseId'])})
            if course:
                enrollment['course'] = serialize_doc(course)
                # Get progress using all possible user IDs
                progress = progress_collection.find_one({
                    '$or': [
                        {'userId': user_id, 'courseId': enrollment['courseId']},
                        {'userId': str(user['_id']), 'courseId': enrollment['courseId']} if user else {'userId': user_id, 'courseId': enrollment['courseId']},
                        {'userId': user.get('clerkId', ''), 'courseId': enrollment['courseId']} if user else {'userId': user_id, 'courseId': enrollment['courseId']}
                    ]
                })
                if progress:
                    enrollment['progress'] = serialize_doc(progress)
        except:
            continue
    return jsonify([serialize_doc(e) for e in enrollments])

# Progress endpoints
@app.route('/api/progress', methods=['POST'])
def update_progress():
    data = request.json
    user_id = data.get('userId')
    course_id = data.get('courseId')
    
    # Try to find user by both user_id and clerk_id
    user = users_collection.find_one({
        '$or': [
            {'clerkId': user_id},
            {'_id': ObjectId(user_id) if ObjectId.is_valid(user_id) else None}
        ]
    })
    
    if user:
        user_id_str = str(user['_id'])
        clerk_id = user.get('clerkId', '')
        # Look for progress using all possible user IDs
        progress = progress_collection.find_one({
            '$or': [
                {'userId': user_id, 'courseId': course_id},
                {'userId': user_id_str, 'courseId': course_id},
                {'userId': clerk_id, 'courseId': course_id}
            ]
        })
    else:
        progress = progress_collection.find_one({
            'userId': user_id,
            'courseId': course_id
        })
    
    if progress:
        completed_topics = data.get('completedTopics', progress.get('completedTopics', []))
        course = courses_collection.find_one({'_id': ObjectId(course_id)})
        total_topics = len(course.get('topics', [])) if course else 1
        progress_percent = (len(completed_topics) / total_topics * 100) if total_topics > 0 else 0
        
        progress_collection.update_one(
            {'_id': progress['_id']},
            {'$set': {
                'completedTopics': completed_topics,
                'progress': progress_percent,
                'lastUpdated': datetime.now(timezone.utc).isoformat()
            }}
        )
        updated = progress_collection.find_one({'_id': progress['_id']})
        return jsonify(serialize_doc(updated))
    return jsonify({'error': 'Progress not found'}), 404

@app.route('/api/progress/user/<user_id>/course/<course_id>', methods=['GET'])
def get_progress(user_id, course_id):
    # Try to find user by both user_id and clerk_id
    user = users_collection.find_one({
        '$or': [
            {'clerkId': user_id},
            {'_id': ObjectId(user_id) if ObjectId.is_valid(user_id) else None}
        ]
    })
    
    if user:
        user_id_str = str(user['_id'])
        clerk_id = user.get('clerkId', '')
        # Look for progress using all possible user IDs
        progress = progress_collection.find_one({
            '$or': [
                {'userId': user_id, 'courseId': course_id},
                {'userId': user_id_str, 'courseId': course_id},
                {'userId': clerk_id, 'courseId': course_id}
            ]
        })
    else:
        progress = progress_collection.find_one({
            'userId': user_id,
            'courseId': course_id
        })
    
    if not progress:
        return jsonify({'error': 'Progress not found'}), 404
    return jsonify(serialize_doc(progress))

# Study updates endpoints
@app.route('/api/study-updates', methods=['POST'])
def create_study_update():
    data = request.json
    update = {
        'userId': data.get('userId'),
        'courseId': data.get('courseId'),
        'content': data.get('content'),
        'date': data.get('date', datetime.now(timezone.utc).isoformat()),
        'verified': False,
        'adminComment': None
    }
    result = study_updates_collection.insert_one(update)
    update['_id'] = str(result.inserted_id)
    return jsonify(serialize_doc(update)), 201

@app.route('/api/study-updates/user/<user_id>', methods=['GET'])
def get_user_study_updates(user_id):
    updates = list(study_updates_collection.find({'userId': user_id}).sort('date', -1))
    # Get course details
    for update in updates:
        course = courses_collection.find_one({'_id': ObjectId(update['courseId'])})
        if course:
            update['course'] = serialize_doc(course)
    return jsonify([serialize_doc(u) for u in updates])

@app.route('/api/study-updates/<update_id>/verify', methods=['PUT'])
def verify_study_update(update_id):
    data = request.json
    study_updates_collection.update_one(
        {'_id': ObjectId(update_id)},
        {'$set': {
            'verified': True,
            'adminComment': data.get('adminComment')
        }}
    )
    update = study_updates_collection.find_one({'_id': ObjectId(update_id)})
    return jsonify(serialize_doc(update))

# Admin endpoints
@app.route('/api/admin/stats', methods=['GET'])
@admin_required()
def get_admin_stats():
    total_courses = courses_collection.count_documents({})
    total_enrollments = enrollments_collection.count_documents({})
    active_students = len(enrollments_collection.distinct('userId'))
    
    # Calculate average completion
    all_progress = list(progress_collection.find({}))
    avg_completion = 0
    if all_progress:
        avg_completion = sum(p.get('progress', 0) for p in all_progress) / len(all_progress)
    
    return jsonify({
        'totalCourses': total_courses,
        'activeStudents': active_students,
        'totalEnrollments': total_enrollments,
        'avgCompletion': round(avg_completion, 0)
    })

@app.route('/api/admin/students', methods=['GET'])
@admin_required()
def get_all_students():
    students = list(users_collection.find({'role': 'student'}))
    for student in students:
        student_id_str = str(student['_id'])
        clerk_id = student.get('clerkId', '')
        
        # Get enrollments using both student ID and clerk ID
        enrollments = list(enrollments_collection.find({
            '$or': [
                {'userId': student_id_str},
                {'userId': clerk_id}
            ]
        }))
        student['enrollments'] = len(enrollments)
        
        # Get progress using both student ID and clerk ID
        progress_list = list(progress_collection.find({
            '$or': [
                {'userId': student_id_str},
                {'userId': clerk_id}
            ]
        }))
        
        if progress_list:
            avg_progress = sum(p.get('progress', 0) for p in progress_list) / len(progress_list)
            student['avgProgress'] = round(avg_progress, 0)
        else:
            student['avgProgress'] = 0
            
        # Get course progress details
        student['courseProgress'] = []
        for progress in progress_list:
            course = courses_collection.find_one({'_id': ObjectId(progress['courseId'])})
            if course:
                student['courseProgress'].append({
                    'courseTitle': course.get('title'),
                    'progress': progress.get('progress', 0),
                    'completedTopics': len(progress.get('completedTopics', [])),
                    'totalTopics': len(course.get('topics', []))
                })
    return jsonify([serialize_doc(s) for s in students])

@app.route('/api/admin/student/<student_id>', methods=['GET'])
@admin_required()
def get_student_details(student_id):
    student = users_collection.find_one({'_id': ObjectId(student_id)})
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    student_id_str = str(student['_id'])
    clerk_id = student.get('clerkId', '')
    
    # Try both student ID and clerk ID for enrollments
    enrollments = list(enrollments_collection.find({
        '$or': [
            {'userId': student_id_str},
            {'userId': clerk_id}
        ]
    }))
    student['enrollments'] = []
    
    for enrollment in enrollments:
        try:
            course = courses_collection.find_one({'_id': ObjectId(enrollment['courseId'])})
            if course:
                progress = progress_collection.find_one({
                    '$or': [
                        {'userId': student_id_str, 'courseId': enrollment['courseId']},
                        {'userId': clerk_id, 'courseId': enrollment['courseId']}
                    ]
                })
                enrollment_data = {
                    'course': serialize_doc(course),
                    'progress': serialize_doc(progress) if progress else None
                }
                student['enrollments'].append(enrollment_data)
        except:
            continue
    
    # Get study updates
    updates = list(study_updates_collection.find({
        '$or': [
            {'userId': student_id_str},
            {'userId': clerk_id}
        ]
    }).sort('date', -1))
    for update in updates:
        try:
            course = courses_collection.find_one({'_id': ObjectId(update['courseId'])})
            if course:
                update['course'] = serialize_doc(course)
        except:
            continue
    student['studyUpdates'] = [serialize_doc(u) for u in updates]
    
    return jsonify(serialize_doc(student))

# Flowise Custom Tools API Endpoints
# These endpoints are called by Flowise custom tools to get user data

@app.route('/api/flowise/user-progress', methods=['POST'])
def get_user_progress_flowise():
    """Endpoint for Flowise 'Get User Progress' custom tool"""
    try:
        data = request.json
        user_id = data.get('userId') or data.get('clerkId') or data.get('sessionId')
        
        if not user_id:
            return jsonify({'error': 'userId, clerkId, or sessionId required'}), 400
        
        # Get user enrollments with progress
        enrollments = list(enrollments_collection.find({
            '$or': [
                {'userId': user_id},
                {'userId': str(user_id)}
            ]
        }))
        
        progress_data = []
        for enrollment in enrollments:
            try:
                course = courses_collection.find_one({'_id': ObjectId(enrollment['courseId'])})
                if course:
                    progress = progress_collection.find_one({
                        '$or': [
                            {'userId': user_id, 'courseId': enrollment['courseId']},
                            {'userId': str(user_id), 'courseId': enrollment['courseId']}
                        ]
                    })
                    
                    progress_data.append({
                        'courseTitle': course.get('title'),
                        'courseId': str(course['_id']),
                        'progress': progress.get('progress', 0) if progress else 0,
                        'completedTopics': len(progress.get('completedTopics', [])) if progress else 0,
                        'totalTopics': len(course.get('topics', [])),
                        'topics': course.get('topics', []),
                        'completedTopicIndices': progress.get('completedTopics', []) if progress else []
                    })
            except:
                continue
        
        return jsonify({
            'userId': user_id,
            'progress': progress_data,
            'totalCourses': len(progress_data)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/flowise/course-recommendations', methods=['POST'])
def get_course_recommendations():
    """Endpoint for Flowise 'Course Recommendations' custom tool"""
    try:
        data = request.json
        user_id = data.get('userId') or data.get('clerkId') or data.get('sessionId')
        
        if not user_id:
            return jsonify({'error': 'userId, clerkId, or sessionId required'}), 400
        
        # Get user's enrolled courses
        enrolled_course_ids = []
        enrollments = list(enrollments_collection.find({
            '$or': [
                {'userId': user_id},
                {'userId': str(user_id)}
            ]
        }))
        enrolled_course_ids = [e['courseId'] for e in enrollments]
        
        # Get all courses
        all_courses = list(courses_collection.find())
        
        # Filter out enrolled courses
        recommended_courses = []
        for course in all_courses:
            if str(course['_id']) not in enrolled_course_ids:
                recommended_courses.append({
                    'courseId': str(course['_id']),
                    'title': course.get('title'),
                    'description': course.get('description'),
                    'instructor': course.get('instructor', 'TBA'),
                    'duration': course.get('duration', 'N/A'),
                    'topicCount': len(course.get('topics', []))
                })
        
        # Get user progress to make smart recommendations
        user_progress = []
        for enrollment in enrollments:
            progress = progress_collection.find_one({
                '$or': [
                    {'userId': user_id, 'courseId': enrollment['courseId']},
                    {'userId': str(user_id), 'courseId': enrollment['courseId']}
                ]
            })
            if progress:
                course = courses_collection.find_one({'_id': ObjectId(enrollment['courseId'])})
                if course:
                    user_progress.append({
                        'course': course.get('title'),
                        'progress': progress.get('progress', 0)
                    })
        
        return jsonify({
            'userId': user_id,
            'recommendedCourses': recommended_courses,
            'currentProgress': user_progress,
            'totalRecommended': len(recommended_courses)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/flowise/user-info', methods=['POST'])
def get_user_info_flowise():
    """Get comprehensive user information for Flowise"""
    try:
        data = request.json
        user_id = data.get('userId') or data.get('clerkId') or data.get('sessionId')
        
        if not user_id:
            return jsonify({'error': 'userId, clerkId, or sessionId required'}), 400
        
        # Get user from database
        user = users_collection.find_one({
            '$or': [
                {'clerkId': user_id},
                {'clerkId': str(user_id)},
                {'_id': ObjectId(user_id) if ObjectId.is_valid(user_id) else None}
            ]
        })
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get enrollments
        enrollments = list(enrollments_collection.find({
            '$or': [
                {'userId': user_id},
                {'userId': str(user_id)},
                {'userId': str(user.get('_id'))}
            ]
        }))
        
        # Get progress summary
        progress_list = list(progress_collection.find({
            '$or': [
                {'userId': user_id},
                {'userId': str(user_id)},
                {'userId': str(user.get('_id'))}
            ]
        }))
        
        avg_progress = 0
        if progress_list:
            avg_progress = sum(p.get('progress', 0) for p in progress_list) / len(progress_list)
        
        return jsonify({
            'userId': user_id,
            'name': user.get('name'),
            'email': user.get('email'),
            'role': user.get('role'),
            'totalEnrollments': len(enrollments),
            'averageProgress': round(avg_progress, 2),
            'enrolledCourses': len(enrollments)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/flowise/user-context', methods=['POST'])
def get_user_context_flowise():
    """Comprehensive user context for Flowise chatbot"""
    try:
        data = request.json
        user_id = data.get('userId') or data.get('clerkId') or data.get('sessionId')
        
        if not user_id:
            return jsonify({'error': 'userId, clerkId, or sessionId required'}), 400
        
        # Get user from database
        user = users_collection.find_one({
            '$or': [
                {'clerkId': user_id},
                {'clerkId': str(user_id)},
                {'_id': ObjectId(user_id) if ObjectId.is_valid(user_id) else None}
            ]
        })
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get enrollments with progress
        enrollments = list(enrollments_collection.find({
            '$or': [
                {'userId': user_id},
                {'userId': str(user_id)},
                {'userId': str(user.get('_id'))}
            ]
        }))
        
        # Get detailed progress for each enrollment
        course_progress = []
        total_progress = 0
        
        for enrollment in enrollments:
            try:
                course = courses_collection.find_one({'_id': ObjectId(enrollment['courseId'])})
                if course:
                    progress = progress_collection.find_one({
                        '$or': [
                            {'userId': user_id, 'courseId': enrollment['courseId']},
                            {'userId': str(user_id), 'courseId': enrollment['courseId']},
                            {'userId': str(user.get('_id')), 'courseId': enrollment['courseId']}
                        ]
                    })
                    
                    progress_data = {
                        'courseTitle': course.get('title'),
                        'courseId': str(course['_id']),
                        'progress': progress.get('progress', 0) if progress else 0,
                        'completedTopics': progress.get('completedTopics', []) if progress else [],
                        'totalTopics': len(course.get('topics', [])),
                        'topics': course.get('topics', []),
                        'enrolledAt': enrollment.get('enrolledAt')
                    }
                    course_progress.append(progress_data)
                    total_progress += progress_data['progress']
            except Exception as e:
                print(f"Error processing enrollment: {e}")
                continue
        
        # Calculate average progress
        avg_progress = total_progress / len(course_progress) if course_progress else 0
        
        # Get study updates
        study_updates = list(study_updates_collection.find({
            '$or': [
                {'userId': user_id},
                {'userId': str(user_id)},
                {'userId': str(user.get('_id'))}
            ]
        }).sort('date', -1).limit(10))
        
        # Get recommended courses (not enrolled)
        enrolled_course_ids = [e['courseId'] for e in enrollments]
        recommended_courses = list(courses_collection.find({
            '_id': {'$nin': [ObjectId(cid) for cid in enrolled_course_ids]}
        }).limit(5))
        
        return jsonify({
            'user': {
                'userId': user_id,
                'name': user.get('name'),
                'email': user.get('email'),
                'role': user.get('role'),
                'createdAt': user.get('createdAt')
            },
            'learning': {
                'totalEnrollments': len(enrollments),
                'averageProgress': round(avg_progress, 2),
                'courseProgress': course_progress,
                'recentStudyUpdates': [{
                    'content': update.get('content'),
                    'date': update.get('date'),
                    'verified': update.get('verified', False)
                } for update in study_updates]
            },
            'recommendations': [{
                'courseId': str(course['_id']),
                'title': course.get('title'),
                'description': course.get('description'),
                'instructor': course.get('instructor', 'TBA')
            } for course in recommended_courses],
            'context': {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'platform': 'ElevateU'
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/flowise/update-progress', methods=['POST'])
def update_progress_flowise():
    """Allow chatbot to update user progress"""
    try:
        data = request.json
        user_id = data.get('userId')
        course_id = data.get('courseId')
        completed_topics = data.get('completedTopics', [])
        
        if not user_id or not course_id:
            return jsonify({'error': 'userId and courseId required'}), 400
        
        # Find user
        user = users_collection.find_one({
            '$or': [
                {'clerkId': user_id},
                {'clerkId': str(user_id)},
                {'_id': ObjectId(user_id) if ObjectId.is_valid(user_id) else None}
            ]
        })
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Update progress
        course = courses_collection.find_one({'_id': ObjectId(course_id)})
        if not course:
            return jsonify({'error': 'Course not found'}), 404
        
        total_topics = len(course.get('topics', []))
        progress_percent = (len(completed_topics) / total_topics * 100) if total_topics > 0 else 0
        
        # Use the existing update_progress logic
        progress_data = {
            'userId': user_id,
            'courseId': course_id,
            'completedTopics': completed_topics,
            'progress': progress_percent,
            'lastUpdated': datetime.now(timezone.utc).isoformat()
        }
        
        # Update or insert progress
        progress_collection.update_one(
            {
                'userId': user_id,
                'courseId': course_id
            },
            {'$set': progress_data},
            upsert=True
        )
        
        return jsonify({
            'success': True,
            'progress': progress_percent,
            'completedTopics': len(completed_topics),
            'totalTopics': total_topics
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/flowise/chat-history', methods=['POST'])
def save_chat_history():
    """Save chat history for context"""
    data = request.json
    # Store in chat_sessions collection
    pass

@app.route('/api/flowise/chat-history/<user_id>', methods=['GET'])
def get_chat_history(user_id):
    """Get previous chat history for context"""
    pass

# Add health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        if db is None:
            return jsonify({
                'status': 'error',
                'message': 'MongoDB not connected',
                'mongodb': False
            }), 503
        
        # Test MongoDB connection
        db.command('ping')
        return jsonify({
            'status': 'healthy',
            'mongodb': True,
            'database': DB_NAME
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'mongodb': False
        }), 503

# ------------------ NEW AGENT POWERED CHATBOT ENDPOINT ------------------

@app.route('/api/chatbot/message', methods=['POST'])
def chatbot_message():
    """ElevateU Agent (Gemini + Mongo + Tools + Memory)"""
    try:
        data = request.json
        message = data.get("message", "")
        user_id = data.get("userId")
        user_name = data.get("userName", "User")
        user_email = data.get("userEmail", "")
        session_id = data.get("sessionId", f"session_{datetime.now().timestamp()}")

        if not message:
            return jsonify({"error": "Message is required"}), 400

        # -------------------------------------------------------
        # 1. SAVE USER MESSAGE TO CHAT HISTORY (same as before)
        # -------------------------------------------------------
        if chat_sessions_collection is not None:
            chat_sessions_collection.update_one(
                {"sessionId": session_id},
                {
                    "$set": {
                        "userId": user_id,
                        "userName": user_name,
                        "userEmail": user_email,
                        "updatedAt": datetime.now(timezone.utc)
                    },
                    "$push": {
                        "messages": {
                            "type": "user",
                            "content": message,
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        }
                    }
                },
                upsert=True
            )

        # -------------------------------------------------------
        # 2. BUILD USER CONTEXT (YOUR ORIGINAL FULL LOGIC)
        # -------------------------------------------------------
        user_context = None
        if user_id and db is not None:
            try:
                user = users_collection.find_one({
                    "$or": [
                        {"clerkId": user_id},
                        {"clerkId": str(user_id)},
                        {"_id": ObjectId(user_id) if ObjectId.is_valid(user_id) else None}
                    ]
                })

                if user:
                    enrollments = list(enrollments_collection.find({
                        "$or": [
                            {"userId": user_id},
                            {"userId": str(user_id)},
                            {"userId": str(user["_id"])}
                        ]
                    }))

                    course_progress = []
                    total_progress = 0

                    for enrollment in enrollments:
                        try:
                            course = courses_collection.find_one({
                                "_id": ObjectId(enrollment["courseId"])
                            })
                            if not course:
                                continue

                            progress = progress_collection.find_one({
                                "$or": [
                                    {"userId": user_id, "courseId": enrollment["courseId"]},
                                    {"userId": str(user_id), "courseId": enrollment["courseId"]},
                                    {"userId": str(user.get("_id")), "courseId": enrollment["courseId"]}
                                ]
                            })

                            if progress and isinstance(progress, dict):
                                p = safe_progress(progress, course)
                            else:
                                p = safe_progress({}, course)

                            # clean completed topics
                            if not isinstance(p["completedTopics"], list):
                                p["completedTopics"] = []
                            else:
                                clean = []
                                for item in p["completedTopics"]:
                                    try:
                                        if isinstance(item, int):
                                            clean.append(item)
                                        elif isinstance(item, str) and item.isdigit():
                                            clean.append(int(item))
                                    except:
                                        continue
                                p["completedTopics"] = clean

                            if not isinstance(p["topics"], list):
                                p["topics"] = []

                            cp = {
                                "courseTitle": str(course.get("title", "Untitled")),
                                "courseId": str(course.get("_id")),
                                "progress": float(p.get("progress", 0)),
                                "completedTopics": p["completedTopics"],
                                "totalTopics": int(p.get("totalTopics", len(course.get("topics", [])))),
                                "topics": p["topics"],
                                "enrolledAt": enrollment.get("enrolledAt")
                            }

                            course_progress.append(cp)
                            total_progress += cp["progress"]

                        except Exception as e:
                            print(f"Error processing enrollment: {e}")
                            continue

                    avg_progress = total_progress / len(course_progress) if course_progress else 0

                    enrolled_ids = [e["courseId"] for e in enrollments]
                    recommended_courses = list(courses_collection.find({
                        "_id": {"$nin": [ObjectId(cid) for cid in enrolled_ids]}
                    }).limit(5))

                    completed_courses = sum(1 for p in course_progress if p["progress"] >= 100)
                    active_courses = sum(1 for p in course_progress if 0 < p["progress"] < 100)

                    enrollment_list = []
                    for enrollment in enrollments:
                        matched = next(
                            (cp for cp in course_progress if cp["courseId"] == enrollment["courseId"]),
                            None
                        )

                        course_obj = {
                            "title": matched.get("courseTitle", "Unknown") if matched else "Unknown",
                            "topics": matched.get("topics", []) if matched else []
                        }

                        enrollment_list.append({
                            "courseId": enrollment.get("courseId"),
                            "enrolledAt": enrollment.get("enrolledAt"),
                            "progress": matched["progress"] if matched else 0,
                            "lastAccessed": enrollment.get("lastAccessed"),
                            "course": course_obj
                        })

                    user_context = {
                        "user": {
                            "userId": user_id,
                            "name": user.get("name"),
                            "email": user.get("email"),
                            "role": user.get("role"),
                            "createdAt": user.get("createdAt")
                        },
                        "learning": {
                            "totalEnrollments": len(enrollments),
                            "averageProgress": round(avg_progress, 2),
                            "completedCourses": completed_courses,
                            "activeCourses": active_courses,
                            "courseProgress": course_progress,
                            "completionRate": round(
                                (completed_courses / len(enrollments) * 100), 1
                            ) if enrollments else 0
                        },
                        "enrollments": enrollment_list,
                        "recommendations": [{
                            "courseId": str(course["_id"]),
                            "title": course.get("title"),
                            "description": course.get("description"),
                            "instructor": course.get("instructor", "TBA"),
                            "topics": course.get("topics", []),
                            "difficulty": course.get("difficulty", "beginner"),
                            "duration": course.get("duration", "4 weeks")
                        } for course in recommended_courses]
                    }

            except Exception as e:
                print("Error building user context:", e)
                user_context = None

        # -------------------------------------------------------
        # 3. PASS MESSAGE INTO THE NEW AI AGENT
        # -------------------------------------------------------
        agent_reply = agent.process_message(
            message=message,
            user_id=user_id
        )

        # -------------------------------------------------------
        # 4. SAVE AGENT RESPONSE INTO CHAT HISTORY
        # -------------------------------------------------------
        if chat_sessions_collection is not None:
            chat_sessions_collection.update_one(
                {"sessionId": session_id},
                {
                    "$push": {
                        "messages": {
                            "type": "agent",
                            "content": agent_reply.get("reply", ""),
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "action": agent_reply.get("action", "none"),
                            "data": agent_reply.get("data", {})
                        }
                    }
                }
            )

        # -------------------------------------------------------
        # 5. RETURN CLEAN RESPONSE TO FRONTEND
        # -------------------------------------------------------
        return jsonify({
            "reply": agent_reply.get("reply", ""),
            "action": agent_reply.get("action", "none"),
            "data": agent_reply.get("data"),
            "sessionId": session_id,
            "userId": user_id,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        print("ERROR in chatbot message:", e)
        return jsonify({
            "reply": "Sorry Ameer, something went wrong.",
            "error": str(e)
        }), 500

# Chat history endpoints
@app.route('/api/chatbot/sessions/<session_id>/history', methods=['GET'])
def get_chatbot_session_history(session_id):
    """Get chat history for a session"""
    try:
        if chat_sessions_collection is None:
            return jsonify({'error': 'Database not connected'}), 503

        session = chat_sessions_collection.find_one({'sessionId': session_id})
        if not session:
            return jsonify({'error': 'Session not found'}), 404

        return jsonify({
            'sessionId': session_id,
            'messages': session.get('messages', []),
            'userId': session.get('userId'),
            'userName': session.get('userName')
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chatbot/user/<user_id>/sessions', methods=['GET'])
def get_user_sessions(user_id):
    """Get all chat sessions for a user"""
    try:
        if chat_sessions_collection is None:
            return jsonify({'error': 'Database not connected'}), 503

        sessions = list(chat_sessions_collection.find(
            {'userId': user_id},
            {'sessionId': 1, 'userName': 1, 'updatedAt': 1, 'messages.0': 1}
        ).sort('updatedAt', -1).limit(10))

        return jsonify([serialize_doc(session) for session in sessions])

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5000, threaded=True)

