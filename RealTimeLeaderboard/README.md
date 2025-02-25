Real Time Leaderboard
The Real Time Leaderboard is a backend API which allows users to register, sign in, submit scores for various games, and view global + game-specific leaderboards in real-time. The system handles score tracking, leaderboard generation, and provides both REST API endpoints for score submission, viewing games etc, and WebSocket connections for real-time updates.
Built with Django + Django REST Framework, Django Channels for the WebSockets protocol, Redis for leaderboard caching and real-time updates, and PostgreSQL for persistent data storage.


#### **To run and test on Windows** 

1) Clone the repo with svn:  
` svn export https://github.com/asiratongue/intermediate-backend-projects/tree/main/RealTimeLeaderboard`

2) Create and activate the virtual environment from terminal with:  
   `python3 -m venv venv`  
   `PS venv\Scripts\activate (on Windows)`
   
3) Install the dependencies from terminal with:  
   `pip install -r requirements.txt`
   
4) Install and configure Redis locally (required for WebSocket connections and leaderboards):  

   `Download from Redis.io`  
   `Start Redis server on default port (6379)`


5) Configure your database settings in settings.py or use a .env file:  
eg:  
`# .env`  
`DB_NAME='your_database_name'`  
`DB_USER='your_database_user'`  
`DB_PASSWORD='your_database_password'`  
`DB_HOST='localhost' # or your remote DB host`  
`DB_PORT='5432'`  

6) Run migrations:   
`python manage.py migrate`

7) Start the Django app:   
`python manage.py runserver`

## API Endpoints

### **Users**
**POST** `/AsimsLeaderboard/register/`  
Register a new user, receive a JWT token.

**POST** `/AsimsLeaderboard/login/`  
User Login, receive a JWT token.

### **Leaderboard Management**
**GET** `/AsimsLeaderboard/viewgames/`  
View all games currently available in the system.

**POST** `/AsimsLeaderboard/submit/<int:id>/`  
Submit game scores for a specific game with ID.
Takes one header argument, "score", with "wins" and "losses" fields.  
e.g -> `{"score": {"wins": 5, "losses": 2}}`

**GET** `/AsimsLeaderboard/view/global/score/`  
View your global ranking across all games.

**GET** `/AsimsLeaderboard/view/game/<int:id>/score/`  
View your ranking for a specific game.

**GET** `/AsimsLeaderboard/view/report/all/`  
View leaderboard for all games (with time period queries).

**GET** `/AsimsLeaderboard/view/report/<int:id>/`  
View leaderboard for a specific game (with time period queries).

## Time Period Filtering

For the leaderboard report endpoints, you must filter by date range using query parameters:
- `?datefrom=YYYY-MM-DD` - Start date for filtering
- `?dateto=YYYY-MM-DD` - End date for filtering

Example: `/AsimsLeaderboard/view/report/all/?datefrom=2023-01-01&dateto=2023-12-31`

## WebSocket Connection

The system provides real-time updates via WebSocket connections. Connect to:

```
ws://localhost:8000/ws/?<your-jwt-token-here>/
```
The websocket is protected via JWT authentication, you can use the same JWT you get from login, unauthorized users will be disconnected.
This allows for real-time updates of the global wins leaderboard, and global winrate leaderboard, whenever new scores are submitted for any game.

## Data Structure

- **User**: Authentication and user details
- **Game**: Information about games available in the system
- **UserGameProfile**: Links users to games with their respective scores and statistics

## Using Redis

The system uses Redis sorted sets to efficiently store and retrieve leaderboard data:
- Game leaderboards are stored as sorted sets with user scores
- Real-time updates are propagated through Redis pub/sub
- Time-filtered queries are optimized using Redis cache

Thank you :)
