The Movie Reservation System is a backend API which allows users to register, sign in, reserve, view, and cancel seats for their chosen movie screenings. Duplicate bookings, as well as different pricing structures, cinema seating structures, and transaction logic is all handled effectively. Admins are given access to two further endpoints, which generate reports on overall business performance and specific Movie Screenings. Admins are given access to an admin control panel (standard Django Admin page), which allows  them to create and edit new movie screenings, add new movies and genres to the database, as well as view all revenue, transactions, and users who are signed up on the app.

Built with Django + Django REST Framework, Amazon AWS for database + cloud storage, utilising Postgresql.  


#### **to run and test on windows** 

1) Clone the repo with svn:  
   `svn export https://github.com/asiratongue/intermediate-backend-projects/tree/main/MovieReservationSystem`

2) Create and activate the virtual environment from terminal with:  
`python3 -m venv venv` 
`PS venv\Scripts\activate (on windows)`

3) Install the dependencies from terminal with:  
`pip install -r requirements.txt`

4) Set up a .env file with your AWS s3 bucket credentials, eg:
 
    `# .env`
    `AWS_ACCESS_KEY_ID='YOUR_ACCESS_KEY_ID'`    
    `AWS_SECRET_ACCESS_KEY='YOUR_AWS_SECRET_ACCESS_KEY'`    
    `AWS_STORAGE_BUCKET_NAME='YOUR_AWS_STORAGE_BUCKET_NAME'`    
    `AWS_S3_REGION_NAME='YOUR_AWS_S3_REGION_NAME'`


5) configure database settings for Django and AWS in your .env:  
	
	`# .env`
	`DB_NAME='your_database_name' 
	`DB_USER='your_database_user' 
	`DB_PASSWORD='your_database_password' 
	`DB_HOST='your-aws-rds-endpoint.region.rds.amazonaws.com' 
	`DB_PORT='5432' `

6) start the django app:  
`python manage.py runserver`


## **Endpoints**


### **Users**

**POST** `/PrinceCharles/register/`   
Register a new user, recieve a JWT code.

**POST** `/PrinceCharles/login/`   
User Login, recieve a JWT code.


### **MovieReservations**

**GET** `'view/<int:id>/`  
View all  information for a specific movie hosted at the cinema


**GET** `viewall/`  
View all movies hosted at the cinema


**GET** `viewscreenings/`
 View all upcoming movie screenings scheduled to air at PCC


 **GET** `viewavailable/<int:id>/`  
View all seats available for a given movie screening (in algebraic notation)

 
**POST** `reserve/<int:id>`/
Reserve seats and tickets for a movie screening with a given movie screening id,
	Takes one header argument, "Seats", followed by chosen seats.  
	 e.g -> '{"seats": ["C1", "F3", "I4"]}'


**GET** `viewtickets/
View tickets and their seats for a booked movie screening with a given movie screening id.  


**POST** `cancel/<int:id>`/
Cancel tickets/seats for a movie screening with a given movie screening id,
	Takes one header argument, "Cancel", followed by booked seats to cancel.  
	e.g -> '{"cancel": ["C3", "H1"]}'


**POST** `Report/all/`
Recieve a report detailing total Cinema revenue, tickets sold as well as who owns them, currently active movie screenings; requires admin permissions.


**POST** `Report/<int:id>/`
Recieve a report detailing info for a specific movie screening; requires admin permissions.


Thank you :)
