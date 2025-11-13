# ElevateU - AI-Powered Learning Platform

A comprehensive learning management system with AI-powered tutoring, progress tracking, and administrative tools.

## Features

- 🎓 **Comprehensive Courses**: Access a wide range of courses across multiple domains
- 🤖 **AI-Powered Tutor**: Get personalized study recommendations using RAG-based AI
- 📈 **Progress Tracking**: Monitor your learning journey with detailed analytics
- 👥 **Admin Dashboard**: Comprehensive tools for course management and student monitoring
- 🔐 **Secure Authentication**: Powered by Clerk
- 💬 **AI Chatbot**: Integrated Flowise chatbot for instant assistance

## Tech Stack

- **Frontend**: React + Vite
- **Backend**: Flask
- **Database**: MongoDB
- **Authentication**: Clerk
- **AI Chatbot**: Flowise

## Prerequisites

- Node.js (v16 or higher)
- Python (v3.8 or higher)
- MongoDB (local or cloud instance)
- Clerk account (for authentication)
- Flowise account (for chatbot)

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Create a `.env` file in the backend directory:
```
MONGO_URI=mongodb://localhost:27017/
DB_NAME=elevateu
```

6. Start the Flask server:
```bash
python app.py
```

The backend will run on `http://localhost:5000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install --legacy-peer-deps
```

3. Create a `.env` file in the frontend directory:
```
VITE_CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key_here
```

4. Start the development server:
```bash
npm run dev
```

The frontend will run on `http://localhost:3000`

## Configuration

### Clerk Authentication

1. Sign up for a Clerk account at https://clerk.com
2. Create a new application
3. Copy your Publishable Key
4. Add it to `frontend/.env` as `VITE_CLERK_PUBLISHABLE_KEY`

### MongoDB

- For local MongoDB: Use `mongodb://localhost:27017/`
- For MongoDB Atlas: Use your connection string from Atlas dashboard

### Flowise Chatbot

The chatbot is already integrated with the provided chatflow ID. To customize:
1. Update the `chatflowid` in `frontend/src/components/ChatBot.jsx`
2. Update the `apiHost` if using a different Flowise instance

## Project Structure

```
ElevateU/
├── backend/
│   ├── app.py              # Flask application
│   ├── requirements.txt    # Python dependencies
│   └── .env               # Environment variables
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── App.jsx        # Main app component
│   │   └── main.jsx       # Entry point
│   ├── package.json       # Node dependencies
│   └── .env              # Environment variables
└── README.md
```

## API Endpoints

### Courses
- `GET /api/courses` - Get all courses
- `POST /api/courses` - Create a new course
- `GET /api/courses/<id>` - Get a specific course
- `PUT /api/courses/<id>` - Update a course
- `DELETE /api/courses/<id>` - Delete a course

### Users
- `POST /api/users` - Create or get user
- `GET /api/users/<clerk_id>` - Get user by Clerk ID

### Enrollments
- `POST /api/enrollments` - Enroll in a course
- `GET /api/enrollments/user/<user_id>` - Get user enrollments

### Progress
- `POST /api/progress` - Update progress
- `GET /api/progress/user/<user_id>/course/<course_id>` - Get progress

### Admin
- `GET /api/admin/stats` - Get admin statistics
- `GET /api/admin/students` - Get all students
- `GET /api/admin/student/<student_id>` - Get student details

## Usage

1. **Landing Page**: Visit the homepage to learn about ElevateU
2. **Sign Up/Login**: Use Clerk authentication to create an account
3. **Student Dashboard**: View enrolled courses and track progress
4. **Browse Courses**: Explore and enroll in available courses
5. **Admin Dashboard**: Manage courses and monitor student progress (admin only)

## Development

### Running in Development Mode

Backend:
```bash
cd backend
python app.py
```

Frontend:
```bash
cd frontend
npm run dev
```

### Building for Production

Frontend:
```bash
cd frontend
npm run build
```

## License

MIT

