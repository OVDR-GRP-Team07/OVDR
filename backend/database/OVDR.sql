CREATE DATABASE `OVDR`;
SHOW DATABASES;
USE `OVDR`;
SHOW tables;

-- SHOW BINARY LOGS;
-- SHOW VARIABLES LIKE 'log_bin_basename';
-- SELECT * FROM alembic_version;
-- DELETE from alembic_version where version_num = 'baae7b92de7c';

-- Stores user credentials and full-body images for virtual try-on
CREATE TABLE `User`(
	`user_id` INT PRIMARY KEY AUTO_INCREMENT,  -- Unique user ID
    `username` VARCHAR(255) NOT NULL UNIQUE,  -- Unique username for authentication
    `password` VARCHAR(255) NOT NULL,  -- Hashed password for security
    `image_path` VARCHAR(255) DEFAULT NULL  -- Stores user's full-body image, initially NULL
);
-- TRUNCATE TABLE `User`;
-- Drop table `User`;
-- ALTER TABLE users CHANGE password_hash password VARCHAR(255) NOT NULL;
-- test user
-- Insert INTO User (username, `password`) VALUES ("zixin",'scrypt:32768:8:1$J19xdJo7dHb3jcuM$eea50a69cd8f6d23a71892f582e950db7770e0bc2c57e8122aaa76f7cb5abd7604b240c03303d05eb64305d0fcc3d71e3750d93f2bc7d90b4e22b05d61b43c31');
Select * from user;
select * from Clothing;
select * from Combination;
TRUNCATE TABLE Combination;
-- ------------------------------------------------------------------------------------------------------------------------------------
-- Drop table Clothing;
-- Stores general clothing items 
CREATE TABLE Clothing (
    cid INT PRIMARY KEY AUTO_INCREMENT,  -- Unique clothing item ID
    category ENUM('tops', 'bottoms', 'dresses') NOT NULL,  -- Clothing categories are extensible
    caption JSON,  -- AI-generated description of the clothing item
    closet_users INT DEFAULT 0,  -- The number of people added to the wardrob, click on the number +1
    cloth_path VARCHAR(255),  -- Path to clothing image
    cloth_mask_path VARCHAR(255),  -- Path to clothing mask image
    model_tryon_path VARCHAR(255),  -- Path to the image with the clothing item applied
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Timestamp for sorting by newest items
);
-- ALTER TABLE Clothing CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- SELECT SCHEMA_NAME, DEFAULT_CHARACTER_SET_NAME FROM information_schema.SCHEMATA WHERE SCHEMA_NAME = 'ovdr';

SELECT * FROM Clothing ORDER BY cid;
-- TRUNCATE TABLE Clothing;  -- AUTO_INCREMENT (The count will reset (primary key fields such as cid will start at 1))
-- -- View data
SELECT * FROM Clothing ORDER BY cid LIMIT 20;
SELECT * FROM Clothing where category = "tops" ORDER BY cid DESC LIMIT 10;
-------------------------------------------------------------------------------------------------------

-- Closet Table: Store closet for users
CREATE TABLE Closet (
    id INT PRIMARY KEY AUTO_INCREMENT,  -- Unique record ID
    user_id INT NOT NULL,  -- User who owns the wardrobe
    clothing_id INT NOT NULL,   -- Clothing item ID
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,   -- Timestamp of when it was added
    FOREIGN KEY (user_id) REFERENCES `User`(user_id),
    FOREIGN KEY (clothing_id) REFERENCES Clothing(cid) ON DELETE CASCADE
);
-- Drop Table `Closet`;
-- Select * from Closet;
-- TRUNCATE TABLE Closet;

-- not used
-- Trigger: Limit wardrobe items to 5 per category
DELIMITER //

CREATE TRIGGER limit_closet_items
AFTER INSERT ON Closet
FOR EACH ROW
BEGIN
    -- Ensure users do not exceed 5 items per category (tops, bottoms, dresses)
    DELETE FROM Closet 
    WHERE user_id = NEW.user_id 
    AND clothing_id IN (SELECT cid FROM Clothing WHERE category = 'tops')
    AND id NOT IN (
        SELECT id FROM (
            SELECT id FROM Closet 
            WHERE user_id = NEW.user_id 
            AND clothing_id IN (SELECT cid FROM Clothing WHERE category = 'tops')
            ORDER BY added_at DESC 
            LIMIT 5
        ) AS temp_table
    );

    -- Make sure `bottoms` do not exceed 5 pieces
    DELETE FROM Closet 
    WHERE user_id = NEW.user_id 
    AND clothing_id IN (SELECT cid FROM Clothing WHERE category = 'bottoms')
    AND id NOT IN (
        SELECT id FROM (
            SELECT id FROM Closet 
            WHERE user_id = NEW.user_id 
            AND clothing_id IN (SELECT cid FROM Clothing WHERE category = 'bottoms')
            ORDER BY added_at DESC 
            LIMIT 5
        ) AS temp_table
    );

    -- Ensure users do not exceed 5 items per category (tops, bottoms, dresses)
    DELETE FROM Closet 
    WHERE user_id = NEW.user_id 
    AND clothing_id IN (SELECT cid FROM Clothing WHERE category = 'dresses')
    AND id NOT IN (
        SELECT id FROM (
            SELECT id FROM Closet 
            WHERE user_id = NEW.user_id 
            AND clothing_id IN (SELECT cid FROM Clothing WHERE category = 'dresses')
            ORDER BY added_at DESC 
            LIMIT 5
        ) AS temp_table
    );
END;

//
DELIMITER ;

-- --------------------------------------------------------------------------------------------------------
-- Stores users' outfit combinations
CREATE TABLE Combination (
    id INT PRIMARY KEY AUTO_INCREMENT,  -- Unique ID
    user_id INT NOT NULL,  -- User who created the outfit
    top_id INT,  -- Selected top item
    bottom_id INT,  -- Selected bottom item
    dress_id INT,  -- Selected dress item
    outfit_path VARCHAR(225) Not Null,  -- Path to the generated outfit image
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES `User`(user_id) ON DELETE CASCADE,
    FOREIGN KEY (top_id) REFERENCES Clothing(cid) ON DELETE SET NULL,
    FOREIGN KEY (bottom_id) REFERENCES Clothing(cid) ON DELETE SET NULL,
    FOREIGN KEY (dress_id) REFERENCES Clothing(cid) ON DELETE SET NULL
);
Use OVDR;
Select * from combination;
select * from `user`;
-- Drop table Combination;
TRUNCATE TABLE Combination;

INSERT INTO Combination (user_id, outfit_path)
VALUES
(3, '/data/combinations/user_3/1.png'),
(3, '/data/combinations/user_3/2.png'),
(3, '/data/combinations/user_3/3.png'),
(3, '/data/combinations/user_3/4.png'),
(3, '/data/combinations/user_3/5.png'),
(3, '/data/combinations/user_3/6.png'),
(3, '/data/combinations/user_3/7.png'),
(3, '/data/combinations/user_3/8.png'),
(3, '/data/combinations/user_3/9.png'),
(3, '/data/combinations/user_3/10.png'),
(3, '/data/combinations/user_3/11.png'),
(3, '/data/combinations/user_3/12.png'),
(3, '/data/combinations/user_3/13.png'),
(3, '/data/combinations/user_3/14.png'),
(3, '/data/combinations/user_3/15.png'),
(3, '/data/combinations/user_3/16.png'),
(3, '/data/combinations/user_3/17.png'),
(3, '/data/combinations/user_3/18.png'),
(3, '/data/combinations/user_3/19.png'),
(3, '/data/combinations/user_3/20.png'),
(3, '/data/combinations/user_3/21.png'),
(3, '/data/combinations/user_3/22.png'),
(3, '/data/combinations/user_3/23.png'),
(3, '/data/combinations/user_3/24.png'),
(3, '/data/combinations/user_3/25.png');

INSERT INTO Combination (user_id, outfit_path)
VALUES
(1, '/data/combinations/user_1/1.png'),
(1, '/data/combinations/user_1/2.png'),
(1, '/data/combinations/user_1/3.png'),
(1, '/data/combinations/user_1/4.png'),
(1, '/data/combinations/user_1/5.png'),
(1, '/data/combinations/user_1/6.png'),
(1, '/data/combinations/user_1/7.png'),
(1, '/data/combinations/user_1/8.png'),
(1, '/data/combinations/user_1/9.png'),
(1, '/data/combinations/user_1/10.png'),
(1, '/data/combinations/user_1/11.png'),
(1, '/data/combinations/user_1/12.png'),
(1, '/data/combinations/user_1/13.png'),
(1, '/data/combinations/user_1/14.png'),
(1, '/data/combinations/user_1/15.png'),
(1, '/data/combinations/user_1/16.png'),
(1, '/data/combinations/user_1/17.png'),
(1, '/data/combinations/user_1/18.png'),
(1, '/data/combinations/user_1/19.png'),
(1, '/data/combinations/user_1/20.png'),
(1, '/data/combinations/user_1/21.png'),
(1, '/data/combinations/user_1/22.png'),
(1, '/data/combinations/user_1/23.png'),
(1, '/data/combinations/user_1/24.png'),
(1, '/data/combinations/user_1/25.png'),
(1, '/data/combinations/user_1/26.png'),
(1, '/data/combinations/user_1/27.png'),
(1, '/data/combinations/user_1/28.png'),
(1, '/data/combinations/user_1/29.png'),
(1, '/data/combinations/user_1/30.png');




-- --------------------------------------------------------------------------------------------------------

-- Tracks user interactions for analytics and recommendations
CREATE TABLE `History` (
    id INT PRIMARY KEY AUTO_INCREMENT,  -- Unique ID
    user_id INT NOT NULL,  -- User who viewed the clothing item
    clothing_id INT NOT NULL,   -- Clothing item ID
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Timestamp of the view event
    FOREIGN KEY (user_id) REFERENCES `User`(user_id) ON DELETE CASCADE,
    FOREIGN KEY (clothing_id) REFERENCES Clothing(cid) ON DELETE CASCADE
);
SELECT * FROM `History`;
-- -- TRUNCATE TABLE `History`;
-- Drop Table `History`;
DELETE FROM History
WHERE user_id = 3;

-- SELECT TABLE_NAME, COLUMN_NAME, CONSTRAINT_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
-- FROM information_schema.KEY_COLUMN_USAGE
-- WHERE TABLE_SCHEMA = 'ovdr' AND TABLE_NAME = 'closet';
-- ALTER TABLE `closet` DROP FOREIGN KEY history_ibfk_1;
-- ALTER TABLE `History` ADD CONSTRAINT history_ibfk_1 FOREIGN KEY (user_id) REFERENCES `User` (user_id) ON DELETE CASCADE;


-- Find out the most popular clothes in the last 7 days, which can be used for home page recommendations
-- SELECT clothing_id, COUNT(*) AS views
-- FROM History
-- WHERE created_at >= NOW() - INTERVAL 7 DAY
-- GROUP BY clothing_id
-- ORDER BY views DESC
-- LIMIT 10;

-- Delete history > 20 each user
-- DELETE FROM `History` 
-- WHERE user_id = 1 
-- AND id NOT IN (
--     SELECT id FROM (
--         SELECT id FROM History
--         WHERE user_id = 1
--         ORDER BY created_at DESC
--         LIMIT 20
--     ) AS temp_table
-- );


-- (x) Automation: EVENT (automatically deletes old records each time it is inserted) 
DELIMITER //

CREATE EVENT limit_history_records
ON SCHEDULE EVERY 1 MINUTE 
DO
BEGIN
    DELETE FROM `History`
    WHERE user_id = NEW.user_id 
    AND id NOT IN (
        SELECT id FROM (
            SELECT id FROM History
            WHERE user_id = NEW.user_id
            ORDER BY created_at DESC
            LIMIT 20
        ) AS temp_table
    );
END;

//
DELIMITER ;

-- ----- All the Tables Below is No Longer Used ------------------------------------------------------------------------

-- -- Separated Clothing Tables is no longer used
-- CREATE TABLE tops (
--     cid INT PRIMARY KEY AUTO_INCREMENT,
--     caption JSON,
--     closet_users INT NOT NULL DEFAULT 0 COMMENT 'XX people added this to Closet',  -- Click to count +1
--     cloth_path VARCHAR(255),
--     cloth_mask_path VARCHAR(255),
--     model_tryon_path VARCHAR(255),
--     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Time when added'  
-- );
-- DROP TABLE `tops`;

-- CREATE TABLE bottoms (
--     cid INT PRIMARY KEY AUTO_INCREMENT,
--     caption JSON, 
--     closet_users INT NOT NULL DEFAULT 0,
--     cloth_path VARCHAR(255),
--     cloth_mask_path VARCHAR(255),
--     model_tryon_path VARCHAR(255),
--     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-- );
-- DROP TABLE `bottoms`;

-- CREATE TABLE dresses (
--     cid INT PRIMARY KEY AUTO_INCREMENT,
--     caption JSON, 
--     closet_users INT NOT NULL DEFAULT 0 COMMENT 'XX people added this to Closet',  -- 点击则数目＋1
--     cloth_path VARCHAR(255),
--     cloth_mask_path VARCHAR(255),
--     model_tryon_path VARCHAR(255),
--     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Time when added'  -- Can choose to see the latest additions when filtering
-- );
-- DROP TABLE `dresses`;

-- ------------------------------------------------------------------------------------------------------------------------------

-- Security questions registration is no longer used
-- CREATE TABLE `security_questions`(
-- 	`question_id` INT PRIMARY KEY AUTO_INCREMENT,  -- Unique identifier for each security question
-- 	`question_text` VARCHAR(255) UNIQUE NOT NULL  -- Security question text
-- );
-- INSERT INTO `security_questions`(`question_text`) VALUES
-- ('Who was your favorite teacher in high school?'),
-- ('What was the name of your first school?'),
-- ('In which city were you born?'),
-- ('Where did you go on your first vacation?'),
-- ('What was the name of the street you grew up on?'),
-- ('What was the name of your first pet?');


-- Stores users' encrypted answers to security questions
-- CREATE TABLE user_security_answers (
--     `answer_id` INT PRIMARY KEY AUTO_INCREMENT,  -- Unique ID for processed images
--     `user_id` INT UNIQUE NOT NULL,  -- User answering the security question
--     `question_id` INT NOT NULL,  -- Security question ID
--     `answer_hash` VARCHAR(255) NOT NULL,  -- hash to store the answer
--     FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,  -- Hashed answer for security
--     FOREIGN KEY (question_id) REFERENCES security_questions(question_id) ON DELETE CASCADE,
--     UNIQUE (user_id, question_id)  -- Ensures a user cannot select the same question multiple times
-- );

-- Drop table security_questions;
-- Drop table users;
-- Drop table user_security_answers;

-- ------------------------------------------------------------------------------------------------------------------------------
-- Drop table processed_images;
-- Stores images processed for virtual try-on; not currently in use
-- CREATE TABLE processed_images (
--     processed_id INT PRIMARY KEY AUTO_INCREMENT,  -- Unique ID for processed images
--     user_id  INT UNIQUE NOT NULL,  -- Each user has only one processed image
--     image_densepose_path VARCHAR(255) NOT NULL,   -- Path to the dense pose image
--     agnostic_mask_path VARCHAR(255) NOT NULL,   -- Path to the agnostic mask image
--     FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
-- );
-- ALTER TABLE processed_images COMMENT = 'Temporarily unused, reserved for future needs. This table stores processed images of users.';