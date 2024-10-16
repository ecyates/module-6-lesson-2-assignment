from flask import Flask, jsonify, request
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
ma = Marshmallow(app)
my_db_password = input("Enter password for the database: ")

def get_db_connection():
    # Database connection parameters
    db_name = "fitness_center_db"
    user = "root"
    password = my_db_password
    host = "localhost"
    try:
        # Attempting to establish a connection
        conn = mysql.connector.connect(
            database = db_name,
            user = user,
            password = password,
            host = host
        )
        #Check if the connection is successful
        return conn
    except Error as e:
        # Handling any connection errors
        print(f"Error: {e}")
        return None

class MemberSchema(ma.Schema):
    '''Defining the Member Schema that takes an id, name, and age from the Fitness Center Database.'''
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    age = fields.Int(required=True)

class WorkoutSessionSchema(ma.Schema):
    '''Defining the Workout Session Schema that takes a session id, member id, date, time, and activity from 
    the Fitness Center Database.'''
    session_id = fields.Int(dump_only=True)
    member_id = fields.Int(required=True) 
    session_date = fields.Date(required=True) 
    session_time = fields.Str(required=True)
    activity = fields.Str(required=True) 

# Instantiating the schemas
member_schema = MemberSchema()
members_schema = MemberSchema(many=True)
workout_session_schema = WorkoutSessionSchema()
workout_sessions_schema = WorkoutSessionSchema(many=True)

# -------------------------------------------------------------------- #
# ADD MEMBER
@app.route("/members", methods=["POST"])
def add_member():
    try: 
        member = member_schema.load(request.json) # Retrieve member from user
    except ValidationError as e: # Handle validation error
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    try:
        conn = get_db_connection() # Connect to the database
        if conn is None: # Handle database error
            return jsonify({"error":"Database connection failed"}), 500
        cursor = conn.cursor()
        query = "INSERT INTO Members (name, age) Values(%s,%s)" # Query to add a new member
        cursor.execute(query, (member['name'], member['age'])) # Execute query
        conn.commit()
        return jsonify({"message":"New member successfully added!"}), 201 # Return success
    except Error as e: # Handle additional errors
        return jsonify({"error":str(e)}), 500
    finally: # Disconnect from database
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


# -------------------------------------------------------------------- #
# UPDATE MEMBER
@app.route("/member/<int:id>", methods=["PUT"])
def update_member(id):
    try: 
        member_data = member_schema.load(request.json) # Retrieve updated member info from user
    except ValidationError as e: # Handle validation errors
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    try: 
        conn = get_db_connection() # Connect to database
        if conn is None: # Handle database errors
            return jsonify({"error":"Database connection failed"}), 500
        cursor = conn.cursor()
        updated_member = (member_data['name'], member_data['age'], id) # Define updated member
        query = "UPDATE Members SET name = %s, age = %s WHERE id = %s" # Query to update member
        cursor.execute(query, updated_member) # Execute query
        conn.commit()        
        return jsonify({"message": "Member updated successfully!"}), 201 # Return success
    except Error as e: # Handle additional errors
        return jsonify({"error":str(e)}), 500
    finally: # Disconnect from database
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# -------------------------------------------------------------------- #
# DELETE MEMBER
@app.route("/member/<int:id>", methods=["DELETE"])
def delete_member(id):
    try: 
        conn = get_db_connection() # Connect to database
        if conn is None: # Handle database error
            return jsonify({"error":"Database connection failed"}), 500
        cursor = conn.cursor()
        query1 = "DELETE FROM WorkoutSessions WHERE member_id = %s" # Query to delete sessions for member
        cursor.execute(query1, (id, )) # Execute first query
        query2 = "DELETE FROM Members WHERE id = %s" # Query to delete member
        cursor.execute(query2, (id, )) # Execute second query
        conn.commit() # Commit
        return jsonify({"message": "Member was successfully deleted!"}), 201 # Return success
    except Error as e: # Handle additional errors
        return jsonify({"error":str(e)}), 500
    finally: # Disconnect from database
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# -------------------------------------------------------------------- #
# GET MEMBER BY NAME
@app.route("/search_members", methods=["GET"])
def search_members():
    member = request.args.get('name') # Retrieve name to search for from user
    try: 
        conn = get_db_connection() # Connect to the database
        if conn is None: # Handle database errors
            return jsonify({"error":"Database connection failed"}), 500
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM Members WHERE name LIKE %s" # Query to search for the member by name
        cursor.execute(query, (f"%{member}%", )) # Execute query 
        members = cursor.fetchall()
        return members_schema.jsonify(members) # Return list of members matching search
    except Error as e: # Handle any additional errors
        return jsonify({"error":str(e)}), 500
    finally: # Disconnect from database
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# -------------------------------------------------------------------- #
# GET ALL MEMBERS
@app.route("/members", methods=["GET"])
def get_members():
    try: 
        conn = get_db_connection() # Connect to database
        if conn is None: # Handle database error
            return jsonify({"error":"Database connection failed"}), 500
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM Members" # Query to retrieve all members from database
        cursor.execute(query) # Execute query
        members = cursor.fetchall()
        return members_schema.jsonify(members) # Return list of all members
    except Error as e: # Handle any additional errors
        return jsonify({"error":str(e)}), 500
    finally: # Disconnect from database
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# -------------------------------------------------------------------- #
# ADD WORKOUT SESSION
@app.route("/workout-sessions", methods=["POST"])
def add_workout_session():
    try: 
        # Retrieve workout session data from the user
        session_data = workout_session_schema.load(request.json) 
    except ValidationError as e: # Handle validation error
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    try:
        conn = get_db_connection() # Connect to database
        if conn is None: # Handle database error
            return jsonify({"error":"Database connection failed"}), 500
        cursor = conn.cursor()
        # Query to add new workout session into the database
        query = "INSERT INTO WorkoutSessions (member_id, session_date, session_time, activity) Values(%s,%s,%s,%s)"
        # Execute query
        cursor.execute(query, (session_data['member_id'], session_data['session_date'], session_data['session_time'], session_data['activity']))
        conn.commit()
        # Return success
        return jsonify({"message":"New workout session successfully added!"}), 201
    except Error as e: # Handle additional errors
        return jsonify({"error":str(e)}), 500
    finally: # Disconnect from database
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
# -------------------------------------------------------------------- #
# UPDATE WORKOUT SESSION
@app.route("/workout-session/<int:id>", methods=["PUT"])
def update_workout_session(id):
    try:  # Retrieve updated workout session data
        session_data = workout_session_schema.load(request.json)
    except ValidationError as e: # Handle validation error
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    try: 
        conn = get_db_connection() # Connect to the database
        if conn is None: # Handle database error
            return jsonify({"error":"Database connection failed"}), 500
        cursor = conn.cursor()
        # Define the updated session based on data retrieved from user
        updated_session = (session_data['member_id'], session_data['session_date'], session_data['session_time'], session_data['activity'], id)
        # Query to update the workout session with provided id
        query = "UPDATE WorkoutSessions SET member_id = %s, session_date = %s, session_time = %s, activity = %s WHERE session_id = %s"
        # Execute query
        cursor.execute(query, updated_session)
        conn.commit()        
        return jsonify({"message": "Workout session updated successfully!"}), 201 # Return success
    except Error as e: # Handle additional errors
        return jsonify({"error":str(e)}), 500
    finally: # Disconnect from database
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
            
# -------------------------------------------------------------------- #
# DELETE WORKOUT SESSION
@app.route("/workout-session/<int:id>", methods=["DELETE"])
def delete_workout_session(id):
    try: 
        conn = get_db_connection() # Connect to database
        if conn is None: # Handle database error
            return jsonify({"error":"Database connection failed"}), 500
        cursor = conn.cursor()
        query = "DELETE FROM WorkoutSessions WHERE session_id = %s" # Query to delete workout session from database
        cursor.execute(query, (id, )) # Execute query
        conn.commit()        
        return jsonify({"message": "Workout session was successfully deleted!"}), 201 # Return success
    except Error as e: # Handle additional errors
        return jsonify({"error":str(e)}), 500
    finally: # Disconnect from database
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
            
# -------------------------------------------------------------------- #
# GET WORKOUT SESSION BY SESSION ID
@app.route("/workout-session/<int:id>", methods=["GET"])
def get_workout_session(id):
    try: 
        conn = get_db_connection() # Connect to database
        if conn is None:
            return jsonify({"error":"Database connection failed"}), 500
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM WorkoutSessions WHERE session_id=%s" # Query to search for session by id
        cursor.execute(query, (id,)) # Execute query
        workout_sessions = cursor.fetchall()
        return workout_sessions_schema.jsonify(workout_sessions) # Return list of sessions matching conditions
    except Error as e: # Handle additional errors
        return jsonify({"error":str(e)}), 500
    finally: # Disconnect from database
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# -------------------------------------------------------------------- #
# GET ALL WORKOUT SESSIONS
@app.route("/workout-sessions", methods=["GET"])
def get_workout_sessions():
    try: 
        conn = get_db_connection() # Connect to database 
        if conn is None: # Handle database error
            return jsonify({"error":"Database connection failed"}), 500
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM WorkoutSessions" # Query to retrieve all workout sessions from database
        cursor.execute(query) # Execute query
        workout_sessions = cursor.fetchall()
        return workout_sessions_schema.jsonify(workout_sessions) # Return all workout sessions
    except Error as e: # Handle additional errors
        return jsonify({"error":str(e)}), 500
    finally: # Disconnect from database
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# -------------------------------------------------------------------- #
# GET WORKOUT SESSIONS BY MEMBER NAME
@app.route("/workout-session-by-member", methods=["POST"])
def workout_session_by_member():
    member = request.json.get('member') # Retrieve member name to search by
    try: 
        conn = get_db_connection() # Connect to database
        if conn is None:
            return jsonify({"error":"Database connection failed"}), 500
        cursor = conn.cursor(dictionary=True)
        # Query to retrieve workout sessions for member name provided
        query = '''
        SELECT s.session_date, s.session_time, s.activity, s.session_id
        FROM WorkoutSessions s, Members m
        WHERE s.member_id = m.id and m.name = %s
        '''
        # Execute query 
        cursor.execute(query, (member,))
        workout_sessions = cursor.fetchall()
        return workout_sessions_schema.jsonify(workout_sessions) # Return all sessions matching conditions
    except Error as e: # Handle errors
        return jsonify({"error":str(e)}), 500
    finally: # Disconnect from database
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
            
if __name__ == "__main__":
    app.run(debug=True)