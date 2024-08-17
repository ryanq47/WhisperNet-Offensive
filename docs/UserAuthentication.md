# User Auth

This is the documentation for the User Authentication Plugin. This plugin handles user authentication.

#### Future/Goals:
- [ ] 2fa if possible


#### Todo:
- [X] user register function
- [X - Review] User Login function ( creates token )
- [ ] look into 2fa/auth options?

- [X] Default args for a user/pass if none specified in DB. 
    currently, registration endpoint is open to anyone. Can change this by disabling registrion endpoint through settings, or doing a jwt_required. 

- [ ] Clean up/re-go over code, then merge into main

# Endpoints

## 1. Login Endpoint

- **URL**: `/login`
- **Method**: `POST`
- **Description**: Authenticates a user and returns an access token if the credentials are correct.

### Request

- **Content-Type**: `application/json`
- **Body**:
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
  - `username`: The username of the user trying to log in.
  - `password`: The password of the user trying to log in.

### Response

- **Content-Type**: `application/json`
- **Body**:
  ```json
  {
    "message": "string",
    "data": {
      "access_token": "string"
    }
  }
  ```

- **Success Response**:
  - **Status Code**: `200 OK`
  - **Response Body**:
    ```json
    {
      "message": "Login Success",
      "data": {
        "access_token": "jwt_access_token"
      }
    }
    ```

- **Error Responses**:
  - **Status Code**: `401 Unauthorized`
    - **Response Body**:
      ```json
      {
        "message": "Login Failure",
        "data": {
          "access_token": ""
        }
      }
      ```
  - **Status Code**: `404 Not Found` (if user not found)
    - **Response Body**:
      ```json
      {
        "message": "Login Failure",
        "data": {
          "access_token": ""
        }
      }
      ```

### Notes

- Logs are maintained for successful and failed login attempts.
- The access token is a JWT token used for authentication in subsequent requests.

---

## 2. Register Endpoint

- **URL**: `/register`
- **Method**: `POST`
- **Description**: Registers a new user. Requires JWT authentication to access.
- **Protection**: JWT required

### Request

- **Content-Type**: `application/json`
- **Body**:
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
  - `username`: The desired username for the new user.
  - `password`: The desired password for the new user.

### Response

- **Content-Type**: `application/json`
- **Body**:
  ```json
  {
    "message": "string",
    "status": "integer"
  }
  ```

- **Success Response**:
  - **Status Code**: `200 OK`
  - **Response Body**:
    ```json
    {
      "message": "User 'username' created successfully",
      "status": 200
    }
    ```

- **Error Responses**:
  - **Status Code**: `400 Bad Request`
    - **Response Body**:
      ```json
      {
        "message": "username and password field are required",
        "status": 400
      }
      ```
  - **Status Code**: `409 Conflict`
    - **Response Body**:
      ```json
      {
        "message": "A user with this username already exists",
        "status": 409
      }
      ```
  - **Status Code**: `410 Gone`
    - **Response Body**:
      ```json
      {
        "message": "Route is disabled",
        "status": 410
      }
      ```


## Configuration settings

There are a few configuration values that are related to this plugin


#### config.yaml
`server.endpoints.enable_registration`: (Bool) Enables/Disables the `/registration` endpoint on the server. Handy for not allowing any new users to be registered.

`server.authentication.bcrypt.rounds`: (int, 1-24) How many rounds of Bcrypt a password will be hashed. The higher the number, the more secure, but computation time will greatly increase. 

`server.authentication.jwt.expiration`: (int) The time (in seconds) until a token expires, after generation. Default is 900 seconds (15 minutes)

#### .env
The .env file has a few other relevant settings:

`JWT_SECRET_KEY`: The secret key used to sign all JWT tokens. *MAKE SURE THIS IS STRONG, AND SECURE!!!!*, otherwise anyone could forge JWT tokens to the server.

`DEFAULT_USERNAME`: If no user exists in the database, the default username to create a user with

`DEFAULT_PASSWORD`: If no user exists in the database, the default password to create a user with



