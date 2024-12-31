Workout Tracker app which allows users to register, sign in, create and schedule Workout Plans from created "exercise sessions" and generate reports on progress and query for created workout plans/exercise sessions.
there are only 10 exercises in the db currently, but an admin feature to add more exercises is easily implemented using djangos built in admin panel. 

Built with Django, and celery task queue for real time scheduler processing.

#### **to run and test on windows** 

git clone 

Create and activate the virtual environment with:
'python3 -m venv venv'
PS venv\Scripts\activate (on windows)

Install the dependencies:
pip install -r requirements.txt 

start the celery worker:
celery -A WorkoutTracker worker -l DEBUG -P solo

start the redis broker on wsl:
sudo service redis-server start

start the django app with 
python manage.py runserver

there is some data and users already within the database, credentials can be found within the example_commands.txt for the respective django apps.

Troubleshooting
To clear redis broker
redis-cli
FLUSHALL
exit

To clear any python/celery processes that may be running in the background and interfering:
taskkill //F //IM python.exe
taskkill //F //IM celery.exe

### **Users**

**POST** /WorkoutTracker/register/ 
Register a new user, recieve a JWT code.

**POST** /WorkoutTracker/login/ 
User Login, recieve a JWT code.


### **Scheduler**

POST schedule/<int:idx>/ 
Schedule a new workout, with the workout session ID of your choice.

POST schedule/
Mark a scheduled workout as pending.

DELETE schedule/remove/<int:idx>/
Delete a Scheduled workout with matching Scheduler Obj ID.

PATCH schedule/update/<int:idx>/
Update a Scheduled workout with matching Scheduler Obj ID, options to update, start_time, duration, and Workout Plan.

GET report/
Get a report on how many workouts you've completed, missed, and a percentage overall of your progress.

GET schedule/search/
Make a query on all your scheduled workouts, you can search by date, and by workout session ID.

GET schedule/list/
Retrieve all Scheduled Workouts.


#### **Workouts**

POST workout/create/
Create a new workout, first creates 'Exercise_Session' objects, given valid exercises, with the right fields set (sets, repetitions, weights).

When making post requests to the '/WorkoutTracker/workout/create/' endpoint, you can either choose to create both a new workout plan and new exercise sessions, a new workout plan with existing exercise session(s), or just some new exercise session(s).
you can also mix and match with newly created exercise sessions, and already existing exercise session keys for the workout plan that you wish to create.

 

GET exercises/
List all exercises available within the database.

GET exercises/<int:id>/
Retrieve information about a specific exercise, given the ID.

DELETE workout/remove/<int:id>/
Delete a workout from the database matching given ID.

PATCH workout/remove/<int:id>/
Update a workout within the database matching given ID.

GET workout/list/
List all workouts within the database.

GET exercise/sessions/
List all exercise sessions created by the user.
