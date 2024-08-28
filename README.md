# User Management API

This project consists of a set of serverless Python functions for managing user data in a PostgreSQL database. The functions include creating, geting, updating, and deleting user records. This guide covers setup, deployment, and usage.

## Setup Instructions

1. **Create a Free Tier Account**
   - Create an account on your preferred cloud provider. AWS is preferred for this project.

2. **Enable Services**
   - **AWS Lambda**: For serverless functions.
   - **Amazon RDS**: For PostgreSQL database .

3. **Database Setup**
   - Create a PostgreSQL database instance.
   - Create the following tables:

     **`users` Table**:
     ```sql
     CREATE TABLE users (
         user_id UUID PRIMARY KEY,
         full_name VARCHAR(255) NOT NULL,
         mob_num VARCHAR(15) NOT NULL,
         pan_num VARCHAR(10) NOT NULL,
         manager_id UUID,
         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
         updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
         is_active BOOLEAN DEFAULT TRUE
     );
     ```

     **`managers` Table**:
     ```sql
     CREATE TABLE managers (
         id UUID PRIMARY KEY,
         name VARCHAR(255) NOT NULL
     );
     ```

   - **Test Data for `managers`**:
     ```sql
     INSERT INTO managers (id, name) VALUES 
     ('550e8400-e29b-41d4-a716-446655440000', 'Nikhil Singh'),
     ('86efba38-2853-4ebf-ab09-b3fa476ea5ec', 'Narendra Singh');
     ```

## Function Endpoints

### 1. **/create_user**

- **Method**: POST
- **API Link**: https://zvdg0yl602.execute-api.ap-south-1.amazonaws.com/create_user
- **Request Body**: 
  ```json
  {
      "full_name": "John Doe",
      "mob_num": "+919876543210",
      "pan_num": "ABCDE1234F",
      "manager_id": "86efba38-2853-4ebf-ab09-b3fa476ea5ec"
  }

  ```

  **Response:**
  - Success: Returns a success message upon successful user creation.
  - Failure: Returns an appropriate error message if any validation fails.

### 2. /get_users

- **Method:** POST
- **API Link:** https://zvdg0yl602.execute-api.ap-south-1.amazonaws.com/get_users
- **Request Body:**
  ```json
  {
    "user_id": "uuid",
    "mob_num": "9876543210"    
  }
  ```
- **Response:**
  - Success: Returns a JSON object with an array of user objects.
  - Failure: Returns an empty JSON array if no users found.

### 3. /delete_user

- **Method:** POST
- **API Link:** https://zvdg0yl602.execute-api.ap-south-1.amazonaws.com/delete_user.
- **Request Body:**
  ```json
  {
    "user_id": "uuid",
    "mob_num": "9876543210"
  }
  ```
- **Response:**
  - Success: Returns a success message upon successful user deletion.
  - Failure: Returns an appropriate error message if user not found.

### 4. /update_user

- **Method:** POST
- **API Link:** https://zvdg0yl602.execute-api.ap-south-1.amazonaws.com/update_user
- **Request Body:**
  ```json
  {
    "user_ids": ["uuid1", "uuid2"],
    "update_data": {
      "full_name": "Updated Name",
      "mob_num": "9876543210",
      "pan_num": "AABCP1234C",
      "manager_id": "uuid"
    }
  }
  ```
  ```json
  {
    "user_ids": ["uuid1"],
    "update_data": {
      "full_name": "Updated Name",
      "mob_num": "9876543210",
      "pan_num": "AABCP1234C",
      "manager_id": "uuid"
    }
  }
  ```
- **Response:**
  - Success: Returns a success message upon successful user update.
  - Failure: Returns an appropriate error message if any validation fails.

## BEST Practices followed-

- Proper error handling and logging are implemented.
- Timely commits are made with meaning full comments to display the project progress.

