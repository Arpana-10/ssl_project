# Portal for the courses

## Overview

We have created a portal where users can register as a student or teacher and based on their identity they can perform different tasks, like a teacher can create courses and assignments, impose deadlines for each assignment, see the submissions made by the students, update marks and feedback for any student for each assignment and many more. Students can register themselves for a course by a unique Course code(shared by teacher), make multiple submissions to assignments of a registered course however only last submitted solution will be considered for grading, and the submissions will be evaluated at the time of submission itself, so that students can improve thier solutions and more to explore. However all these functionalites are accessable in authenticated sessions only.


## TechStack

**Django (Python)** : for both frontend and backend, however designed the frontend UI using HTML, CSS and Java script

**SQLite (as database)**: for data storage  

## Commands to operate

Clone the repository and go inside the demo folder, the current structure would be like:

> demo/\
  users/\
  media/\
  manage.py
  
 Then run these commands:

`python3 manage.py makemigrations`

the makemigrations command basically generates the SQL commands for the users app. It does not execute those commands in the database file. So tables are not created after makemigrations.

`python3 manage.py migrate`

migrate executes those SQL commands in the database file. So after executing migrate all the tables of the installed apps are created in the database file.

`python3 manage.py runserver`

This starts the Django development server. Now that the server’s running, visit http://127.0.0.1:8000/ with your web browser. 


## Features implemented

The following features have been implemented in this project:

#### Log in and sign up

Users can sign up and then log in. Any data relevant to a user can only be accessed in **authenticated** sessions only.
Then users get redirected to specific homepage, depending on whether the identity of the user is teacher or student.

#### Profile Update

Users will be able to change their passwords, only if they provide correect initial password.

#### Create Course and Assignment

Users with identity as teacher can create a course by providing the title for the course and a unique code gets generated for the course, which can be used by other users to register for the course. The teacher can create assignments for each course. Creating an assignment requires a assignment file (problem statement), name of the assignment, specifying the file type to be uploaded as solution for that assignment, if the required filetype is **.zip** or **.tgz** then a a text file with the output of **tree command** for the submission, else if the required filetype is **.sh** then a **.zip** file consisting of the test cases and autograder script (**.sh** file) as the **autograder** and finally specifying the deadline for that assignment.  

#### Download all the submissions

Teacher can download each submission made for an assignment individually as well as  all together in a zip file

#### Update marks and Feedback for each submission via a CSV file 

Teacher can download the marks and feedback of all students in a **CSV** file and update their marks and feedback and then upload the updated CSV file to update the marks and feedback for each submission in the database.
#### Update marks and Feeadback for each assignment via the website

Teacher can just fill the feeback and marks form form for any assignment to update it on the go.

#### Register for a course

Users with identity as student can register themselves for a course by having the **code** for that course.

#### Access all assignments and Upload solutions

Students registered for a course can view all the assignments and make multiple submissions to it. However only the **latest** submission will be accessible by the teacher.

#### File Type Checking

Before saving any file in the database, the file type is getting checked wherever only a particular range of file types are allowed

#### Autograder for each submission

As soon as a student uploads a solution, first the file type gets verified and if the file type is **.sh**, the autograder runs on the solution file and updates the marks and feedback for that submission.

#### Tree Structure check

As soon as a student uploads a solution, first the file type gets verified and if the file type is **.zip** or **.tgz**, the tree structure for that submission gets verified and the marks and feedback for that submission gets updated accordingly. 
> `Note:` The students are required to put all the required files and folders inside a folder and compress that **single** folder to any required type extension and then make submission of the created archive file.

#### Pending Assignments

In the homepage students can see all the assignments of all the courses it has registered for, which are still due (no submission made and the deadline is not yet over) 

#### Deregister Students

A teacher can deregister any student registered for a course from that course.


## Conclusion

Our portal is going to be the **moodle** of future generations :P
