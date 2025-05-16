README: FLASK BACKEND - SETUP
1. 
cd backend

2.
python -m venv venv        # Create virtual environment
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

3.
pip install -r requirements.txt

4.
export FLASK_APP=app.py
export FLASK_ENV=development

5.
flask db upgrade   # or run your database initialization script

6.
flask run
The backend API should now be running at:
http://localhost:5000


1.
REACT FRONTEND - SETUP

2.
npm install

3.
npm start

The frontend should now be running at:
http://127.0.0.1:3000/



4. Using the application
Open your browser and navigate to http://localhost:3000 to access the React frontend.

The frontend communicates with the backend API running on port 5000.

The backend uses SQLite3 as its database.



##################################################################
Troubleshooting
Ensure that ports 3000 (frontend) and 5000 (backend) are free.
##################################################################
If you encounter issues with virtual environments or package installations, verify your Python and Node.js versions.

Check that your .env or environment variables are set correctly for Flask if your app requires configuration.

When using http://localhost:3000 chrome might not save the coockies, its recommended to use http://127.0.0.1:3000/ instead.
