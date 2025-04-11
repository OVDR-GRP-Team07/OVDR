# OVDR Database Documentation

## Overview
The **OVDR** (Online Virtual Dressing Room) database is designed to store user information, virtual try-on data, and clothing items. It supports features like:
- User information (user name, hash password and full body image)
- Clothing item storage with corresponding text descriptions (captions)
- Virtual try-on outfit combinations
- User wardrobe (Closet) management
- History tracking

---

## Database Schema
The following tables are included in the **OVDR** database (obsolete or temporarily unused tables are not included):

### **1. `users` (User Table)**
Stores user credentials and profile data.

| Column         | Type              | Constraints                      | Description                          |
|---------------|------------------|---------------------------------|--------------------------------------|
| `user_id`     | INT (PK, AUTO_INCREMENT) | Primary key | Unique ID for each user |
| `username`    | VARCHAR(255)      | UNIQUE, NOT NULL               | Unique username for login |
| `password_hash` | VARCHAR(255)     | NOT NULL                        | Hashed password |
| `image_path`  | VARCHAR(255)      | DEFAULT NULL                    | Path to user's full-body image |

---

### **2. `clothing` (Clothing Items)**
Stores clothing data and AI-generated descriptions.

| Column         | Type              | Constraints                      | Description |
|---------------|------------------|---------------------------------|-------------|
| `cid`        | INT (PK, AUTO_INCREMENT) | Primary key | Unique clothing item ID |
| `category`   | ENUM('tops', 'bottoms', 'dresses') | NOT NULL | Clothing category |
| `caption`    | JSON | NULL | AI-generated clothing description |
| `closet_users` | INT | DEFAULT 0 | Number of users who added this to wardrobe |
| `cloth_path` | VARCHAR(255) | NOT NULL | Path to clothing image |

---

### **3. `closet` (User Wardrobe)**
Tracks clothing items added to users' wardrobes.

| Column       | Type   | Constraints | Description |
|-------------|--------|-------------|-------------|
| `id`        | INT (PK, AUTO_INCREMENT) | Primary key | Record ID |
| `user_id`   | INT   | NOT NULL, FK → `users(user_id)` | User who owns this wardrobe |
| `clothing_id` | INT | NOT NULL, FK → `clothing(cid)` ON DELETE CASCADE | Clothing item |

#### **Trigger: Limit closet items to 5 per category**
```sql
DELIMITER //
CREATE TRIGGER limit_closet_items
AFTER INSERT ON Closet
FOR EACH ROW
BEGIN
    DELETE FROM Closet
    WHERE user_id = NEW.user_id
    AND id NOT IN (
        SELECT id FROM (
            SELECT id FROM Closet
            WHERE user_id = NEW.user_id
            ORDER BY added_at DESC
            LIMIT 5
        ) AS temp_table
    );
END;
//
DELIMITER ;
```

---

### **4. `history` (User View History)**
Tracks which clothing items users have viewed.

| Column       | Type   | Constraints | Description |
|-------------|--------|-------------|-------------|
| `id`        | INT (PK, AUTO_INCREMENT) | Primary key | Record ID |
| `user_id`   | INT   | NOT NULL, FK → `users(user_id)` | User who viewed clothing |
| `clothing_id` | INT | NOT NULL, FK → `clothing(cid)` ON DELETE CASCADE | Clothing item |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Timestamp of viewing |

#### **Trigger: Automatically keep only the latest 20 records**
```sql
DELIMITER //
CREATE TRIGGER limit_history_records
AFTER INSERT ON `history`
FOR EACH ROW
BEGIN
    DELETE FROM `history`
    WHERE user_id = NEW.user_id
    AND id NOT IN (
        SELECT id FROM (
            SELECT id FROM history
            WHERE user_id = NEW.user_id
            ORDER BY created_at DESC
            LIMIT 20
        ) AS temp_table
    );
END;
//
DELIMITER ;
```

---

## **Entity Relationship Diagram (ERD)**
![ERD Diagram](ERD.png)

---

## **Common Queries**
- **Get user’s recent wardrobe items:**
  ```sql
  SELECT * FROM Closet WHERE user_id = 1 ORDER BY added_at DESC LIMIT 5;
  ```
- **Find the most viewed clothing in the last 7 days:**
  ```sql
  SELECT clothing_id, COUNT(*) AS views FROM history
  WHERE created_at >= NOW() - INTERVAL 7 DAY
  GROUP BY clothing_id
  ORDER BY views DESC
  LIMIT 10;
  ```

---

### **Conclusion**
This documentation provides a complete overview of the **OVDR database schema**, its relationships, constraints, and queries. Future improvements may include indexing optimizations and scalability enhancements.