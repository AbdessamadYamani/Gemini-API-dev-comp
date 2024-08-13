import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import plotly.graph_objects as go
import random
import google.generativeai as genai
from langchain.tools import tool
from crewai import Crew
from agents import AllAgents
from tasks import AllTasks
import sys
from crewai.process import Process
from settings import api_configs as config

# Initialize Firebase app (if not already initialized)
if not firebase_admin._apps:
    cred = credentials.Certificate(r'C:\Users\user\Documents\Gemini API dev comp\back_end\compgemini-ee7f5-firebase-adminsdk-qk6r8-68d4bbd760.json')
    firebase_admin.initialize_app(cred)

# Get a reference to the Firestore database
db = firestore.client()

# Reference to the 'User' collection
users_ref = db.collection('User')

# Reference to the 'Courses' collection
courses_ref = db.collection('Courses')

def sign_in(email, password):
    # Implement your sign-in logic here
    # For demonstration, we'll just check if the user exists
    user = users_ref.where('user_email', '==', email).where('user_password', '==', password).get()
    return len(user) > 0

def register_user(user_data):
    doc_ref = users_ref.document()
    doc_ref.set(user_data)
    return doc_ref.id

def show_dashboard(user_id):
    st.header("Dashboard")

    # Fetch user's enrolled courses and progress from Firestore
    enrolled_courses_ref = db.collection('Courses_Enrolled').where('User_ID', '==', user_id)
    enrolled_courses_data = {doc.id: doc.to_dict() for doc in enrolled_courses_ref.stream()}

    if not enrolled_courses_data:
        st.write("You are not enrolled in any courses yet.")
        return

    # Display enrolled courses and progress
    st.subheader("Your Enrolled Courses")
    
    course_names = []
    progress_values = []

    for course_id, course_data in enrolled_courses_data.items():
        course_ref = courses_ref.document(course_data['Course_ID'])
        course_info = course_ref.get().to_dict()
        if course_info:
            course_name = course_info.get('Course_name', 'Unknown Course')
            progress = course_data.get('Progress', 0) * 100
            st.write(f"- {course_name} ({progress:.2f}%)")
            
            course_names.append(course_name)
            progress_values.append(progress)

    # Create a bar chart for course progress
    if course_names and progress_values:
        fig = go.Figure(data=[go.Bar(
            x=course_names,
            y=progress_values,
            text=[f"{p:.1f}%" for p in progress_values],
            textposition='auto',
        )])
        fig.update_layout(
            title="Course Progress",
            xaxis_title="Course",
            yaxis_title="Progress (%)",
            yaxis=dict(range=[0, 100])
        )
        st.plotly_chart(fig)
    else:
        st.write("No course data available to display in the chart.")

    # Recommendations (random courses)
    st.subheader("Recommended Courses")

    # Fetch all courses from Firestore
    all_courses_ref = courses_ref.stream()
    all_courses = [course.to_dict() for course in all_courses_ref]

    # Select 3 random courses
    recommended_courses = random.sample(all_courses, 3)

    # Display the recommended courses in a horizontal layout
    cols = st.columns(3)
    for i, course in enumerate(recommended_courses):
        with cols[i]:
            course_card = f"""
            <div class="course-card">
                <img src="{course['Course_Image_Url']}" class="course-image" style="width: 250px; height: 250px;">
                <h3>{course['Course_name']}</h3>
                <div class="course-meta">
                    Level: {course['Course_Level']} | Rating: {course['Course_rating']}
                </div>
                <div class="course-progress">
                    Progress: 0%
                </div>
            </div>
            """
            st.markdown(course_card, unsafe_allow_html=True)
            if st.button(f"Start Learning: {course['Course_name']}", key=f"recommend_btn_{i}"):
                st.session_state.selected_course = course
                st.session_state.current_page = "course_details"
                st.rerun()

def show_courses(user_id):
    st.header("Available Courses")

    # Add a search bar
    search_query = st.text_input("Search Courses", "")

    # Add filters
    col1, col2 = st.columns(2)
    with col1:
        selected_level = st.selectbox("Filter by Level", ["All", "Beginner", "Intermediate", "Advanced"])
    with col2:
        selected_rating = st.slider("Filter by Rating", 0.0, 5.0, (0.0, 5.0), step=0.5)

    # Fetch courses from Firestore
    courses_query = courses_ref
    if search_query:
        courses_query = courses_query.where("Course_name", ">=", search_query).where("Course_name", "<=", search_query + "\uf8ff")
    if selected_level != "All":
        courses_query = courses_query.where("Course_Level", "==", selected_level)
    courses = courses_query.stream()

    # Fetch user's enrolled courses and progress from Firestore
    enrolled_courses_collection = db.collection('Courses_Enrolled')
    enrolled_courses_ref = enrolled_courses_collection.where('User_ID', '==', user_id)
    enrolled_courses_data = {doc.to_dict()['Course_ID']: doc.to_dict() for doc in enrolled_courses_ref.stream()}

    # Create a 3x3 grid layout
    col1, col2, col3 = st.columns(3)
    cols = [col1, col2, col3]
    course_count = 0

    for course in courses:
        course_data = course.to_dict()
        course_data['Course_ID'] = course.id
        course_id = course.id
        if course_data["Course_rating"] >= selected_rating[0] and course_data["Course_rating"] <= selected_rating[1]:
            with cols[course_count % 3]:
                course_card = f"""
                <div class="course-card">
                    <img src="{course_data['Course_Image_Url']}" class="course-image" style="width: 250px; height: 250px;">
                    <h3>{course_data['Course_name']}</h3>
                    <div class="course-meta">
                        Level: {course_data['Course_Level']} | Rating: {course_data['Course_rating']}
                    </div>
                    <div class="course-progress">
                        Progress: {enrolled_courses_data.get(course_id, {"Progress": 0.0})["Progress"] * 100:.2f}%
                    </div>
                </div>
                """
                st.markdown(course_card, unsafe_allow_html=True)
                if st.button(f"Start Learning: {course_data['Course_name']}", key=f"btn_{course_data['Course_name']}"):
                    # Create a new document in the Courses_Enrolled collection
                    new_doc_ref = enrolled_courses_collection.document()
                    new_doc_ref.set({
                        'Course_ID': course_id,
                        'Progress': 0.0,
                        'User_ID': user_id
                    })

                    st.session_state.selected_course = course_data
                    st.session_state.current_page = "course_details"
                    st.rerun()
            course_count += 1

        # Break after displaying 9 courses
        if course_count >= 9:
            break

    if course_count == 0:
        st.write("No courses found matching your criteria.")

def show_course_details(user_id):
    if 'selected_course' not in st.session_state:
        st.error("No course selected. Please go back to the courses page.")
        return

    course = st.session_state.selected_course
    course_id = course.get('Course_ID')
    if not course_id:
        st.error("Course ID not found in the selected course. Please try selecting the course again.")
        if st.button("Back to Courses"):
            st.session_state.current_page = "courses"
            st.rerun()
        return

    # Fetch user's enrolled courses and progress from Firestore
    enrolled_courses_collection = db.collection('Courses_Enrolled')
    enrolled_courses_ref = enrolled_courses_collection.where('User_ID', '==', user_id).where('Course_ID', '==', course_id)
    enrolled_course_data = next(enrolled_courses_ref.stream(), None)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.title(course['Course_name'])
        st.write(f"**Level:** {course['Course_Level']}")
        st.write(f"**Description:** {course['Course_description']}")

        st.subheader("Learning Path")
        for step in course['Learning_Path'].split('\n'):
            st.write(step)

        if st.button("Start Learning"):
            if enrolled_course_data:
                enrolled_course_data.reference.update({'Progress': 1.0})
            else:
                new_doc_ref = enrolled_courses_collection.document()
                new_doc_ref.set({
                    'Course_ID': course_id,
                    'Progress': 1.0,
                    'User_ID': user_id
                })

            st.session_state.current_page = "chat_interface"
            st.rerun()

    with col2:
        st.image(course['Course_Image_Url'], width=200)
        st.write(f"**Rating:** {course['Course_rating']}/5.0")
        if enrolled_course_data:
            st.write(f"**Progress:** {enrolled_course_data.to_dict()['Progress'] * 100:.2f}%")
        else:
            st.write(f"**Progress:** 0%")

    if st.button("Back to Courses"):
        st.session_state.current_page = "courses"
        st.rerun()
def enroll_in_course(user_id, course_id):
    course_ref = courses_ref.document(course_id)
    course_data = course_ref.get().to_dict()
    learning_path = course_data['Learning_Path'].split('\n')
    
    progress_data = {f"step_{i+1}": 0 for i in range(len(learning_path))}
    
    enrolled_courses_collection = db.collection('Courses_Enrolled')
    new_doc_ref = enrolled_courses_collection.document()
    new_doc_ref.set({
        'Course_ID': course_id,
        'User_ID': user_id,
        'Progress': progress_data
    })

def show_chat_interface():
    st.title("Learning Chat Interface")

    # Create a container for the learning path and progress bars
    path_container = st.container()

    with path_container:
        st.subheader(f"{st.session_state.selected_course['Course_name']} Learning Path")

        # Fetch the user's progress in the selected course
        enrolled_courses_collection = db.collection('Courses_Enrolled')
        enrolled_courses_ref = enrolled_courses_collection.where('User_ID', '==', st.session_state.user_id).where('Course_ID', '==', st.session_state.selected_course['Course_ID'])
        enrolled_course_data = next(enrolled_courses_ref.stream(), None)

        if enrolled_course_data:
            progress_data = enrolled_course_data.to_dict().get('Progress', 0)
            if isinstance(progress_data, dict):
                progress_dict = progress_data
            else:
                progress_dict = {}
                total_progress = float(progress_data)
        else:
            progress_dict = {}
            total_progress = 0

        # Display the learning path and progress
        steps = st.session_state.selected_course['Learning_Path'].split('\n')
        cols = st.columns(len(steps))
        for i, (step, col) in enumerate(zip(steps, cols)):
            with col:
                st.write(f"Step {i+1}: {step}")
                if isinstance(progress_dict, dict):
                    progress = progress_dict.get(f"step_{i+1}", 0) * 100
                else:
                    progress = total_progress * 100
                st.progress(progress / 100)

    st.divider()  # Add a visual separator

    # Chat interface
    chat_container = st.container()

    # Initialize chat history if it doesn't exist
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Initialize CrewAI components
    all_agents = AllAgents(openai_api_key=config.openai_api_key)
    all_tasks = AllTasks(openai_api_key=config.openai_api_key)
    teacher_agent = all_agents.teacher_agent()
    verified_agent = all_agents.verified_agent()
    helper_agent=all_agents.helper_agent()

    # Check if initial message has been sent
    if "initial_message_sent" not in st.session_state:
        st.session_state.initial_message_sent = False

    # If initial message hasn't been sent, generate and display it
    if not st.session_state.initial_message_sent:
        with st.spinner("Generating initial message..."):

            Teacher_task = all_tasks.Teacher_task(teacher_agent)
            verified_agent.tools=[]
            teacher_agent.tools=[Coorection,get_user_and_course_info]

            Teacher_task.tools=[Coorection,get_user_and_course_info]
            # Create the crew with the task
            crew = Crew(
                agents=[teacher_agent],
                tasks=[Teacher_task],
                cache=True,
                manager_agent=verified_agent
            )

            try:
                result = crew.kickoff()
                st.session_state.messages.append({"role": "assistant", "content": result})
                st.session_state.initial_message_sent = True
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                error_message = f"I apologize, but I encountered an error while generating the initial message. Error details: {str(e)}"
                st.session_state.messages.append({"role": "assistant", "content": error_message})

    # Display chat messages from history
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("What is your question?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Get user and course information


        # Create the task with the crew_input parameter
        Teacher_task = all_tasks.Teacher_task(teacher_agent)
        verified_agent.tools=[Coorection,get_user_and_course_info]
        teacher_agent.tools=[Coorection,get_user_and_course_info]

        Teacher_task.tools=[Coorection,get_user_and_course_info]
        # Create the crew with the task
        crew = Crew(
            agents=[teacher_agent],
            tasks=[Teacher_task],
            cache=True,
             manager_agent=verified_agent

        )

        # Run CrewAI and capture its output
        with st.spinner("Generating response..."):
            try:
                result = crew.kickoff()

                # Add the teacher's response to the chat history
                st.session_state.messages.append({"role": "assistant", "content": result})
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                error_message = f"I apologize, but I encountered an error while processing your request. Error details: {str(e)}"
                st.session_state.messages.append({"role": "assistant", "content": error_message})

        # Rerun the app to display the new messages
        st.rerun()

    # Ensure the path_container stays at the top
    st.markdown(
        """
        <style>
        [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
            position: sticky;
            top: 0;
            background-color: white;
            z-index: 999;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
@tool("Decide the learning path")
def Coorection():
    """
  This tools helps to know if the user can go to the next chapter.it have 0 parameters
    """
    History=get_recent_chat_history()
    user_course_infos=get_user_course_info()
    genai.configure(api_key="AIzaSyDPZ2G97ri3vLM3773usRxNw1A22Yi0c60")
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(f"""
 you should explain the course based on the user and course inofs , explain based on the user backstory and hobbies to make it easy for it ,also give the course with 4 examples and 4 exercices in multiple choices and wait for the user to answer using this 
the examples and the exeercices should be based on what you explain on the first section
You will get a conversation between a teacher that explain a course and a student your work is to correct , give score and decide if the user should go to the next chapter or no .
Or based on the chat history choose what is the best answer to the user.
if the user answer correctly mention the next chapter name based on the Current Course: section. 
History of chat : {History}
infos about the user and the course: {user_course_infos}
(the user can choose to go to an other chapter )
if the user answers wrond say it to him .

expected_output=
The result should be in markdown format with 3 section , course section (4 paragraphes) , examples and exercices , the examples and exercices should be related to the part that you explained in the course section. Mnetion the chapter number .

----------------------------

Otherwise the talk normaly with the user
""")
    print("DONE")
    return response.text
def get_recent_chat_history():
    """
    This tool retrieves the last 6 messages from the chat history, labeling user messages and responses the tool is with out parameters.
    """
    if "messages" not in st.session_state or not st.session_state.messages:
        return "No chat history available."
    
    recent_messages = st.session_state.messages[-10:]  # Get the last 6 messages
    formatted_history = []
    
    for message in recent_messages:
        role = message.get("role", "")
        content = message.get("content", "")
        if role == "user":
            formatted_history.append(f"User: {content}")
        elif role == "assistant":
            formatted_history.append(f"Assistant: {content}")
    
    return "\n\n".join(formatted_history)
def get_user_course_info():
    """
    Use this tool to get the data of the current user and the chosen course.
    """
    print("tttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttt")
    if 'user_id' not in st.session_state or 'selected_course' not in st.session_state:
        return "User or course information not available."

    user_id = st.session_state.user_id
    selected_course = st.session_state.selected_course

    # Fetch user data from Firestore
    try:
        user_doc = users_ref.document(user_id).get()
        if not user_doc.exists:
            return "User data not found."
        user_data = user_doc.to_dict()
    except Exception as e:
        return f"Error fetching user data: {str(e)}"

    # Get user's enrolled courses
    try:
        enrolled_courses_ref = db.collection('Courses_Enrolled').where('User_ID', '==', user_id)
        enrolled_courses = enrolled_courses_ref.stream()
    except Exception as e:
        return f"Error fetching enrolled courses: {str(e)}"

    courses_info = []
    for enrolled_course in enrolled_courses:
        course_data = enrolled_course.to_dict()
        course_id = course_data.get('Course_ID')
        if course_id:
            course_doc = courses_ref.document(course_id).get()
            if course_doc.exists:
                course_info = course_doc.to_dict()
                progress = course_data.get('Progress', 0) * 100
                courses_info.append(f"- {course_info.get('Course_name', 'Unknown Course')} (Progress: {progress:.2f}%)")

    user_and_courses_info = f"""
User Information:
- First Name: {user_data.get('user_firstname', 'N/A')}
- Last Name: {user_data.get('user_lastname', 'N/A')}
- Email: {user_data.get('user_email', 'N/A')}
- Phone Number: {user_data.get('user_phonenumber', 'N/A')}
- Backstory: {user_data.get('user_backstory', 'N/A')}
- Hobbies: {user_data.get('user_hobbies', 'N/A')}


Current Course:
- Name: {selected_course.get('Course_name', 'N/A')}
- Description: {selected_course.get('Course_description', 'N/A')}
- Learning Path: {selected_course.get('Learning_Path', 'N/A')}
"""
    return user_and_courses_info.strip()
@tool("get user and course infos")
def get_user_and_course_info():
    """
    Use this tool to get the data of the current user and the chosen course.
    """
    print("tttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttt")
    if 'user_id' not in st.session_state or 'selected_course' not in st.session_state:
        return "User or course information not available."

    user_id = st.session_state.user_id
    selected_course = st.session_state.selected_course

    # Fetch user data from Firestore
    try:
        user_doc = users_ref.document(user_id).get()
        if not user_doc.exists:
            return "User data not found."
        user_data = user_doc.to_dict()
    except Exception as e:
        return f"Error fetching user data: {str(e)}"

    # Get user's enrolled courses
    try:
        enrolled_courses_ref = db.collection('Courses_Enrolled').where('User_ID', '==', user_id)
        enrolled_courses = enrolled_courses_ref.stream()
    except Exception as e:
        return f"Error fetching enrolled courses: {str(e)}"

    courses_info = []
    for enrolled_course in enrolled_courses:
        course_data = enrolled_course.to_dict()
        course_id = course_data.get('Course_ID')
        if course_id:
            course_doc = courses_ref.document(course_id).get()
            if course_doc.exists:
                course_info = course_doc.to_dict()
                progress = course_data.get('Progress', 0) * 100
                courses_info.append(f"- {course_info.get('Course_name', 'Unknown Course')} (Progress: {progress:.2f}%)")

    user_and_courses_info = f"""
User Information:
- First Name: {user_data.get('user_firstname', 'N/A')}
- Last Name: {user_data.get('user_lastname', 'N/A')}
- Email: {user_data.get('user_email', 'N/A')}
- Phone Number: {user_data.get('user_phonenumber', 'N/A')}
- Backstory: {user_data.get('user_backstory', 'N/A')}
- Hobbies: {user_data.get('user_hobbies', 'N/A')}



Current Course:
- Name: {selected_course.get('Course_name', 'N/A')}
- Description: {selected_course.get('Course_description', 'N/A')}
- Learning Path: {selected_course.get('Learning_Path', 'N/A')}
"""
    return user_and_courses_info.strip()

def show_manage_account(user_id):
    st.header("Manage Account")

    # Fetch user data from Firestore
    user_doc = users_ref.document(user_id).get()
    user_data = user_doc.to_dict()

    # Display user information
    st.subheader("Your Account Details")
    st.write(f"First Name: {user_data['user_firstname']}")
    st.write(f"Last Name: {user_data['user_lastname']}")
    st.write(f"Email: {user_data['user_email']}")
    st.write(f"Phone Number: {user_data['user_phonenumber']}")
    st.write(f"Backstory: {user_data['user_backstory']}")
    st.write(f"Hobbies: {user_data['user_hobbies']}")

    # Allow user to update their profile
    st.subheader("Update Your Profile")
    new_firstname = st.text_input("First Name", value=user_data['user_firstname'])
    new_lastname = st.text_input("Last Name", value=user_data['user_lastname'])
    new_email = st.text_input("Email", value=user_data['user_email'])
    new_phone = st.text_input("Phone Number", value=user_data['user_phonenumber'])
    new_backstory = st.text_area("Backstory", value=user_data['user_backstory'])
    new_hobbies = st.text_input("Hobbies (comma-separated)", value=user_data['user_hobbies'])

    if st.button("Save Changes"):
        # Update user data in Firestore
        user_doc.reference.update({
            'user_firstname': new_firstname,
            'user_lastname': new_lastname,
            'user_email': new_email,
            'user_phonenumber': new_phone,
            'user_backstory': new_backstory,
            'user_hobbies': new_hobbies
        })
        st.success("Your profile has been updated.") 
def get_connected_user_and_courses_info():
    if 'user_id' not in st.session_state or not st.session_state.user_id:
        return "No user is currently connected."
    
    user_doc = users_ref.document(st.session_state.user_id).get()
    if not user_doc.exists:
        return "User data not found."
    
    user_data = user_doc.to_dict()
    
    # Get user's enrolled courses
    enrolled_courses_ref = db.collection('Courses_Enrolled').where('User_ID', '==', st.session_state.user_id)
    enrolled_courses = enrolled_courses_ref.stream()
    
    courses_info = []
    for enrolled_course in enrolled_courses:
        course_data = enrolled_course.to_dict()
        course_id = course_data['Course_ID']
        course_doc = courses_ref.document(course_id).get()
        if course_doc.exists:
            course_info = course_doc.to_dict()
            progress = course_data.get('Progress', 0) * 100
            courses_info.append(f"- {course_info['Course_name']} (Progress: {progress:.2f}%)")
    
    user_and_courses_info = f"""
Connected User Information:
- First Name: {user_data.get('user_firstname', 'N/A')}
- Last Name: {user_data.get('user_lastname', 'N/A')}
- Email: {user_data.get('user_email', 'N/A')}
- Phone Number: {user_data.get('user_phonenumber', 'N/A')}
- Backstory: {user_data.get('user_backstory', 'N/A')}
- Hobbies: {user_data.get('user_hobbies', 'N/A')}

Enrolled Courses:
{chr(10).join(courses_info) if courses_info else "No courses enrolled"}
"""
    return user_and_courses_info.strip()


@tool("Create general report from the user project description")
def general_report():
    """
    Give to this tool the Job description and it will return a report of the client project architecture.
    """
    user_and_courses_info = get_connected_user_and_courses_info()    
    genai.configure(api_key="AIzaSyDPZ2G97ri3vLM3773usRxNw1A22Yi0c60")
    model = genai.GenerativeModel('gemini-1.5-pro')
    response = model.generate_content(f"""
Explain to this user this course based on the learning path and it s bobbies + interrests 

User and Courses Information:
{user_and_courses_info}

""")
    return response.text

@tool("get the answer of the user")
def interactive_learning_chat():
    """
    This tool is used to get the last answer provided by the user.
    """
    if "messages" in st.session_state and st.session_state.messages:
        # Iterate through messages in reverse order
        for message in reversed(st.session_state.messages):
            if message["role"] == "user":
                print(message)
                return message["content"]
            
    
    return "No user message found in the chat history."

def main():
    st.set_page_config(layout="wide")  # Set the page to wide mode
    st.title("Learning Platform")

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "dashboard"
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None

    if not st.session_state.logged_in:
        tab1, tab2 = st.tabs(["Sign In", "Register"])

        with tab1:
            st.header("Sign In")
            email = st.text_input("Email", key="signin_email")
            password = st.text_input("Password", type="password", key="signin_password")
            if st.button("Sign In"):
                if sign_in(email, password):
                    # Fetch user ID from Firestore
                    user = users_ref.where('user_email', '==', email).where('user_password', '==', password).get()[0]
                    st.session_state.user_id = user.id
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Invalid credentials")

        with tab2:
            st.header("Register")
            new_user = {}
            new_user['user_firstname'] = st.text_input("First Name", key="reg_firstname")
            new_user['user_lastname'] = st.text_input("Last Name", key="reg_lastname")
            new_user['user_email'] = st.text_input("Email", key="reg_email")
            new_user['user_password'] = st.text_input("Password", type="password", key="reg_password")
            new_user['user_phonenumber'] = st.text_input("Phone Number", key="reg_phone")
            new_user['user_backstory'] = st.text_area("Your Backstory", key="reg_backstory")
            new_user['user_hobbies'] = st.text_input("Hobbies (comma-separated)", key="reg_hobbies")
            new_user['course_progress'] = {}  # Initialize course progress dictionary

            if st.button("Register"):
                user_id = register_user(new_user)
                st.session_state.user_id = user_id
                st.session_state.logged_in = True
                st.rerun()

    else:
        # Sidebar for navigation
        with st.sidebar:
            st.header("Navigation")
            if st.button("Dashboard"):
                st.session_state.current_page = "dashboard"
            if st.button("Courses"):
                st.session_state.current_page = "courses"
            if st.button("Learning Plan"):
                st.session_state.current_page = "learning_plan"
            if st.button("Manage Account"):
                st.session_state.current_page = "manage_account"
            if st.button("Settings"):
                st.session_state.current_page = "settings"
            if st.button("Log Out"):
                st.session_state.logged_in = False
                st.session_state.user_id = None
                st.rerun()

        # Main content area
        if st.session_state.current_page == "dashboard":
            show_dashboard(st.session_state.user_id)
        elif st.session_state.current_page == "courses":
            show_courses(st.session_state.user_id)
        elif st.session_state.current_page == "course_details":
            show_course_details(st.session_state.user_id)
        elif st.session_state.current_page == "chat_interface":
            show_chat_interface()
        elif st.session_state.current_page == "learning_plan":
            st.header("Learning Plan")
            st.write("Your learning plan will be shown here.")
        elif st.session_state.current_page == "manage_account":
            st.header("Manage Account")
            show_manage_account(st.session_state.user_id)
        elif st.session_state.current_page == "settings":
            st.header("Settings")
            st.write("Settings options will be shown here.")

if __name__ == "__main__":
    main()