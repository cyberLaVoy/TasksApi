# To-do List App Documentation

## Resources:

#### todos
##### Attributes:
* short_description
* long_description
* priority
* desired_completion_date
* due_date
* date_entered
* completion_status


#### users
##### Attributes:
* email
* encrypted_password
* fname
* lname


#### sessions
##### Attributes:
* rowid (from users table, when authenticated)
* any temporary data


## Database Schema:
```SQL
CREATE TABLE to_dos
(short_description VARCHAR(63),
 long_description VARCHAR(255),
 priority INTEGER,
 desired_completion_date DATE,
 due_date DATE,
 date_entered DATE,
 completion_status BOOLEAN);


CREATE TABLE users
(email VARCHAR(255),
 encrypted_password VARCHAR(255),
 fname VARCHAR(255),
 lname VARCHAR(255));
```

## REST Endpoints:
Name | HTTP Method | Path
------------ | ------------- | -------------
List | GET | /todos
Retrieve | GET | /todos/todoID
Create | POST | /todos
Create | POST | /users
Create | POST | /sessions
Replace | PUT | /todos/todoID
Delete | DELETE | /todos/todoID


## Password Hashing Method:
#### passlib (bcrypt)
