# API Documentation

## API Overview
This project includes multiple RESTful API modules, each responsible for a specific feature of the OVDR system:

- **Authentication API**: Handle user login, registration, and verification.

- **User Image API**: Upload and retrieve user full-body images.

- **Closet API**: Browse clothing items, manage personal closet selections.

- **History API**: Track and retrieve user's browsing history.

- **Try-On API**: Generate virtual try-on results using StableVITON.

- **Search API**: Perform text-based search over clothing items with CLIP model.

- **Recommendation API**: Recommend popular or personalized clothing.

- **Combination API**: Save and view outfit combinations created by users.

- **Email API**: Send try-on result images to users via email.

Each module lives in `./backend/routes/` and provides clearly defined endpoints documented below.


## 🔐 1. Authentication API (`routes/auth.py`)
> Manage user login and registration logic
### `POST /login` 

**Description**: Authenticate user using username and password.

**Form Data**:
| Field    | Type   | Required | Description             |
|----------|--------|----------|-------------------------|
| username | string | Yes      | The user's username     |
| password | string | Yes      | Plaintext password input|

**Response**:
```json
{
  "success": "Login successful!",
  "username": "testuser",
  "user_id": 1
}
```

**Error Responses**:
- `400 Bad Request` - Username does not exist
- `400 Bad Request` - Password entered incorrectly
- `400 Bad Request` - Invalid input (form validation failed)

---

### `POST /register`

**Description**: Register a new user with a unique username and encrypted password.

**Form Data**:
| Field    | Type   | Required | Description         |
|----------|--------|----------|---------------------|
| username | string | Yes      | Unique username     |
| password | string | Yes      | Password to encrypt |

**Response**:
```json
{
  "message": "User registration succeeded!"
}
```

**Error Response**:
```json
{
  "error": [["Username already exists."]]
}
```

---

### `GET /captcha/email`

**Description**: Sends a 4-digit verification code to the provided email address. (To be integrated into registration in future)

**Query Parameters**:
| Name  | Type   | Required | Description            |
|-------|--------|----------|------------------------|
| email | string | Yes      | Email to receive code  |

**Response**:
```text
success
```

---

### `GET /test`

**Description**: Test email sending (hardcoded email). For development/debugging purposes.

**Response**:
```text
Send successfully
```

## 👤 2. User Image API (`routes/user_image.py`)
> Upload or retrieve user full-body photos
### `POST /upload_image`

**Description**: Upload a user full-body image and update the database with the saved path.

**Form Data**:

| Field    | Type   | Required | Description               |
|----------|--------|----------|---------------------------|
| user_id  | int    | Yes      | ID of the user            |
| file     | file   | Yes      | Image file to be uploaded |

**Response**:
```json
{
  "message": "Image uploaded and path updated successfully",
  "image_path": "data/users/image/1.jpg"
}
```

**Errors**:
- 400: Missing fields or empty file
- 404: User not found

---

### `GET /get_user_info`

**Description**: Retrieve user profile information including the uploaded image path.

**Query Parameters**:

| Name     | Type | Required | Description       |
|----------|------|----------|-------------------|
| user_id  | int  | Yes      | ID of the user    |

**Response**:
```json
{
  "user_id": 1,
  "username": "alice",
  "image_path": "data/users/image/1.jpg"
}
```

**Errors**:
- 400: Missing user_id
- 404: User not found

---

## 🧥 3. Closet API (`routes/closet.py`)

> Endpoints for browsing and managing virtual clothing closet.

---

### `GET /api/clothes`

**Description**: Retrieve all clothing items filtered by category.

**Query Parameters**:

| Name     | Type   | Required | Description                                 |
|----------|--------|----------|---------------------------------------------|
| category | string | No       | Clothing category: `tops`, `bottoms`, `dresses` (default: `tops`) |

**Response**:
```json
{
  "message": "Success",
  "items": [
    {
      "id": 1,
      "title": "Red Floral Cotton Blouse with v-neckline and short sleeves",
      "image_path": "http://localhost:5000/data/clothes/tops/model-tryon/00001.jpg",
      "closet_users": 3
    }
  ]
}
```

---

### `GET /detail/<clothing_id>`

**Description**: Retrieve detailed info about a specific clothing item.

**Path Parameters**:

| Name         | Type | Description         |
|--------------|------|---------------------|
| clothing_id  | int  | Clothing item ID    |

**Response**:
```json
{
  "message": "Success",
  "item": {
    "id": 1,
    "labels": ["red", "floral", "cotton", "blouse"],
    "title": "Red Floral Cotton Blouse with v-neckline and short sleeves",
    "cloth_path": "http://localhost:5000/data/clothes/tops/cloth/00001.jpg"
  }
}
```

---

### `POST /add-to-closet`

**Description**: Add a clothing item to a user's closet.

**Request Body**:
```json
{
  "user_id": 1,
  "clothing_id": 5
}
```

**Constraints**:
- A user can have **up to 5 items per category**.
- Duplicate additions are not allowed.

**Success Response**:
```json
{
  "message": "Item added to closet successfully!"
}
```

**Error Responses**:
```json
{
  "error": "Item already in closet!"
}
```
```json
{
  "error": "Max 5 tops items allowed. Remove one to add new."
}
```

---

### `GET /get-closet`

**Description**: Get all clothing items in a user's closet, optionally filtered by category.

**Query Parameters**:

| Name     | Type   | Required | Description                        |
|----------|--------|----------|------------------------------------|
| user_id  | int    | Yes      | ID of the user                    |
| category | string | No       | Category to filter (default: tops) |

**Response**:
```json
{
  "message": "Success",
  "closet": [
    {
      "id": 5,
      "category": "tops",
      "url": "http://localhost:5000/data/clothes/tops/cloth/00005.jpg"
    }
  ]
}
```

---

### `POST /remove-from-closet`

**Description**: Remove a clothing item from a user's closet.

**Request Body**:
```json
{
  "user_id": 1,
  "clothing_id": 5
}
```

**Response**:
```json
{
  "message": "Item removed from closet successfully."
}
```

---

### `GET /data/clothes/<path:filename>`

**Description**: Serve static clothing images from the `/data/clothes/` directory.

**Example Request**:
```
GET /data/clothes/tops/model-tryon/00001.jpg
```

**Response**:
- Returns the image directly if found.
- HTTP 404 if the image is missing.
---

## 🕘 4. History API (`routes/history.py`)
> Track and retrieve browsing history

### `POST /add-history`

**Description**:  
Adds a clothing item to the user's browsing history.  
- Prevents duplicate entries.
- Keeps only the latest 20 records per user.

**Request Body** (JSON):
```json
{
  "user_id": 1,
  "clothing_id": 5
}
```

**Response**:
```json
{
  "message": "History recorded successfully."
}
```

**Errors**:
- `400`: Missing `user_id` or `clothing_id`.
- `500`: Database error or insertion failure.

---

### `GET /get-history`

**Description**:  
Retrieves the latest 20 items viewed by a specific user from their browsing history.

**Query Parameters**:

| Name     | Type | Required | Description       |
|----------|------|----------|-------------------|
| user_id  | int  | Yes      | ID of the user    |

**Example Request**:
```
GET /get-history?user_id=1
```

**Response**:
```json
{
  "message": "Success",
  "history": [
    {
      "id": 5,
      "image": "http://localhost:5000/data/clothes/tops/cloth/00005_top.jpg",
      "title": "Red Floral Cotton Blouse with round neckline and long sleeves",
      "created_at": "2024-03-30 14:23:12",
      "closet_users": 7,
      "category": "tops"
    }
  ]
}
```

**Errors**:
- `400`: Missing `user_id`.
- `500`: Database error or malformed caption field.



## ✨ 5. Try-On API (`routes/process.py`)
> Generate virtual try-on results

### `POST /process_image`

**Description**:  
Generate a virtual try-on image by combining a user-uploaded full-body image and a selected clothing item.

You can either:
- Provide `item_id` (recommended): automatically fetch clothing from database.
- OR provide `cloth_url` directly (e.g., from frontend image selection).

**Request Body (JSON)**:

| Field         | Type   | Required | Description                                                              |
|---------------|--------|----------|--------------------------------------------------------------------------|
| user_id       | int    | ✅ Yes   | ID of the user                                                           |
| item_id       | int    | ❌ No    | Closet item ID to fetch clothing from DB                                 |
| cloth_url     | string | ❌ No    | Optional: URL or path to clothing image                                  |
| item_category | string | ✅ Yes   | Type of clothing: "tops", "bottoms", or "dresses"                        |

> ⚠️ Either `item_id` or `cloth_url` must be provided.

**Example**:

```json
{
  "user_id": 1,
  "item_id": 15,
  "item_category": "tops"
}
```

**Success Response**:

```json
{
  "message": "success",
  "image_path": "0000012.jpg"
}
```

**Error Responses**:

- `400 Bad Request`: Missing required fields or image
- `404 Not Found`: User or image not found
- `500 Internal Server Error`: StableVITON failure or file I/O issues

---

### `GET /data/clothes/<filename>`

**Description**:  
Serve static clothing images from the `/data/clothes/` directory.

**Example**:  
Request: `GET /data/clothes/tops/cloth/000001_top.jpg`

Returns: Clothing image file.

---

## 🔍 6. Search API (`routes/search.py`)
> Text-based clothing search  

### `GET /search`

**Description**:  
Search for clothing items using a natural language text query. The backend uses a pretrained CLIP model to match text to clothing image embeddings.

**Query Parameters**:

| Name     | Type   | Required | Description                                     |
|----------|--------|----------|-------------------------------------------------|
| query    | string | ✅ Yes   | Natural language query (e.g. "red hoodie")      |
| top_n    | int    | ❌ No    | Number of results to return (default: 20)       |

**Response**:
Returns an array of matched clothing items ranked by similarity.

```json
{
  "items": [
    {
      "id": 12,
      "title": "Red Cotton Hoodie",
      "category": "tops",
      "image_path": "http://localhost:5000/data/clothes/tops/cloth/00012_top.jpg",
      "closet_users": 3
    },
    ...
  ]
}
```

**Errors**:

| Code | Description                               |
|------|-------------------------------------------|
| 400  | Missing query parameter                   |
| 500  | Internal error (model failure, DB error)  |

---


## 🎯 7. Recommendation API (`routes/recommend.py`)
> Recommend popular items or personalized content  

### `GET /clothing/{id}`
- **Description:** Retrieve clothing details
- **Response:**
```json
{
  "id": 1,
  "name": "White Blouse",
  "category": "tops"
}
```

### `GET /recommend/{clothing_id} `
- **Description:** Retrieve top visually and semantically similar clothing items.
- **Response:**
```json
{
  "recommendations": [
    {
      "id": 12,
      "url": "http://localhost:5000/data/clothes/tops/000045_top.jpg"
    }
  ]
}
```

### `GET /recommend/popular`
- **Description:** Retrieve globally popular clothing items based on interaction frequency.
- **Response:**
```json
{
  "recommended_popular": [
    {
      "id": 88,
      "category": "bottoms",
      "url": "http://localhost:5000/data/clothes/bottoms/000088_bottom.jpg"
    }
  ]
}
```

### `GET /recommend/user/{user_id}`
- **Description:** Recommend clothing items for a user based on collaborative filtering.
- **Response:**
```json
{
  "personalized_recommendations": [
    {
      "id": 73,
      "category": "dresses",
      "url": "http://localhost:5000/data/clothes/dresses/000073_dress.jpg"
    }
  ]
}
```

---

## 🧵 8. Combination API (`routes/combination.py`)
> Save try-on results, show and delete outfit combinations 

### `POST /save-combination`

**Description**: Save a virtual try-on combination to the database.

**Request Body (JSON)**:

| Field        | Type   | Required | Description                                 |
|--------------|--------|----------|---------------------------------------------|
| user_id      | int    | ✅ Yes   | ID of the user                              |
| top_id       | int    | ❌ No    | ID of the top clothing item                 |
| bottom_id    | int    | ❌ No    | ID of the bottom clothing item              |
| dress_id     | int    | ❌ No    | ID of the dress item                        |
| resultImage  | string | ✅ Yes   | Relative path to the generated try-on image |

**Response Example**:

```json
{
  "message": "Combination saved!"
}
```

---

### `GET /get-combinations`

**Description**: Retrieve all saved try-on combinations for a given user.

**Query Parameters**:

| Name     | Type | Required | Description       |
|----------|------|----------|-------------------|
| user_id  | int  | ✅ Yes   | ID of the user    |

**Response Example**:

```json
{
  "message": "Success",
  "combinations": [
    {
      "id": 12,
      "top_id": 3,
      "bottom_id": 5,
      "dress_id": null,
      "url": "data/combinations/user_1/000023.jpg"
    }
  ]
}
```

---
### `DELETE /delete-combination`

**Description**:  
Delete a previously saved outfit combination by its ID.

**Request Body**:
```json
{
  "id": 12
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id    | int  | ✅ Yes   | The ID of the combination to delete |

**Response (Success)**:
```json
{
  "message": "Combination deleted successfully."
}
```

**Error Responses**:
- `400 Bad Request`:  
  ```json
  { "error": "Missing combination ID" }
  ```

- `404 Not Found`:  
  ```json
  { "error": "Combination not found" }
  ```

- `500 Internal Server Error`:  
  ```json
  { "error": "Database error or deletion failed" }
  ```

---

### `GET /show_image/<userid>/<filename>`

**Description**: Serve generated outfit image from the `/data/combinations/user_<userid>/` folder.

**Path Parameters**:

| Name     | Type   | Description                                |
|----------|--------|--------------------------------------------|
| userid   | int    | User ID, used to locate the user directory |
| filename | string | File name of the image (URL-encoded if needed) |

**Example**:
```
GET /show_image/1/000003.jpg
```

Returns: The image file if found.

---

## 📩 9. Email API (`routes/email.py`)

### `POST /send-email`

**Description**:  
Send a try-on result image to a specified email address. This endpoint expects a base64-encoded image (JPEG) and recipient email.

**Request Body**:
```json
{
  "email": "user@example.com",
  "imageBase64": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD..."
}
```

**Response**:
- On success:
```json
{
  "success": true,
  "message": "Email sent successfully!"
}
```

- On error:
```json
{
  "success": false,
  "message": "Missing email or image"
}
```

**Notes**:
- Make sure your Flask app is configured with SMTP credentials:
  ```python
  MAIL_SERVER = "smtp.qq.com"
  MAIL_PORT = 465
  MAIL_USERNAME = "your_email@qq.com"
  MAIL_PASSWORD = "your_app_password"
  MAIL_USE_SSL = True
  ```

- You must initialize Flask-Mail and register `email_bp` in `create_app()`.