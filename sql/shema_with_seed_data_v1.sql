DROP DATABASE IF EXISTS forum;
CREATE DATABASE forum 
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
USE forum;

SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;
SET default_storage_engine = InnoDB;


CREATE TABLE `roles` (
  role_id        INT NOT NULL AUTO_INCREMENT,
  role_name      VARCHAR(20) NOT NULL UNIQUE,
  PRIMARY KEY (role_id)
);


CREATE TABLE `users` (
  user_id         INT NOT NULL AUTO_INCREMENT,
  first_name      VARCHAR(32) NOT NULL,
  last_name       VARCHAR(32) NOT NULL,
  email           VARCHAR(254) NOT NULL UNIQUE,
  username        VARCHAR(16) NOT NULL UNIQUE,
  password_hash   VARCHAR(255) NOT NULL,
  role_id         INT NOT NULL,
  is_blocked      BOOLEAN NOT NULL DEFAULT FALSE,
  PRIMARY KEY (user_id),
  FOREIGN KEY (role_id) REFERENCES roles (role_id) ON DELETE RESTRICT,
  CONSTRAINT first_name_length CHECK (CHAR_LENGTH(first_name) >= 2),
  CONSTRAINT last_name_length CHECK (CHAR_LENGTH(last_name) >= 2),
  CONSTRAINT username_length CHECK (CHAR_LENGTH(username) >= 2)
);


CREATE TABLE `topics` (
  topic_id         INT NOT NULL AUTO_INCREMENT,
  author_id        INT NOT NULL,
  title            VARCHAR(128) NOT NULL,
  content          VARCHAR(8192) NOT NULL,
  created_at       DATETIME NOT NULL DEFAULT NOW(),
  is_private       BOOLEAN NOT NULL DEFAULT FALSE,
  is_locked        BOOLEAN NOT NULL DEFAULT FALSE,
  PRIMARY KEY (topic_id),
  FOREIGN KEY (author_id) REFERENCES users (user_id) ON DELETE RESTRICT,
  CONSTRAINT title_length CHECK (CHAR_LENGTH(title) >= 16),
  CONSTRAINT topics_content_length CHECK (CHAR_LENGTH(content) >= 32)
);


CREATE TABLE `replies` (
  reply_id         INT NOT NULL AUTO_INCREMENT,
  topic_id         INT NOT NULL,
  author_id        INT NOT NULL,
  content          VARCHAR(8192) NOT NULL,
  created_at       DATETIME NOT NULL DEFAULT NOW(),
  PRIMARY KEY (reply_id),
  FOREIGN KEY (topic_id) REFERENCES topics (topic_id) ON DELETE CASCADE, 
  FOREIGN KEY (author_id) REFERENCES users (user_id) ON DELETE RESTRICT,
  CONSTRAINT replies_content_length CHECK (CHAR_LENGTH(content) >= 2)
);


CREATE TABLE `reply_votes` (
  user_id            INT NOT NULL,
  reply_id           INT NOT NULL,
  vote               TINYINT NOT NULL,
  PRIMARY KEY (user_id, reply_id),
  FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
  FOREIGN KEY (reply_id) REFERENCES replies (reply_id) ON DELETE CASCADE,
  CONSTRAINT vote_value CHECK (vote IN (1, -1))
);


CREATE TABLE `best_replies` (
  topic_id           INT NOT NULL,
  reply_id           INT NOT NULL,
  PRIMARY KEY (topic_id),
  FOREIGN KEY (topic_id) REFERENCES topics (topic_id) ON DELETE CASCADE,
  FOREIGN KEY (reply_id) REFERENCES replies (reply_id) ON DELETE CASCADE
);


CREATE TABLE `topic_members` (
  topic_id          INT NOT NULL,
  user_id           INT NOT NULL,
  PRIMARY KEY (topic_id, user_id),
  FOREIGN KEY (topic_id) REFERENCES topics (topic_id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
);




INSERT INTO `roles` (role_id, role_name)
VALUES
  (1, 'admin'),
  (2, 'user'),
  (3, 'moderator');


INSERT INTO `users` (user_id, first_name, last_name, email, username, password_hash, role_id, is_blocked)
VALUES 
  (1, 'Aleksandar', 'Shunev', 'shunev@example.com', 'a7shunev', 'pretend it is a hash', 1, FALSE),
  (2, 'Sophia', 'Sotirova', 'skincare_master@example.com', 'sophia_92820', 'pretend it is a hash', 1, FALSE),
  (3, 'Stoyan', 'Mezinov', 'mezinov@example.com', 's.mezinov', 'pretend it is a hash', 1, FALSE),
  (4, 'Tsvetozar', 'Cherkezov', 'zarko@example.com', 'zarko123', 'pretend it is a hash', 2, FALSE),
  (5, 'Nora',  'Andonova',  'nora_a@example.com',  'nora',  'pretend it is a hash', 2, FALSE),
  (6, 'Petar',  'Georgiev', 'petar@example.com',  'petar_g',   'pretend it is a hash', 2, FALSE),
  (7, 'Konstantin',  'Valchanov',   'koko@example.com',  'koko',   'pretend it is a hash', 2, FALSE),
  (8, 'Spam',   'Bot',      'spam@example.com',   'spammer',   'pretend it is a hash', 2, TRUE),
  (9, 'Nikola', 'Petrov',   'nikola@example.com', 'nikola_mod','pretend it is a hash', 3, FALSE);


INSERT INTO `topics` (topic_id, author_id, title, content, is_private)
VALUES
  (1, 2, 'Which are the best 2026 advent calendars?', 'Hi guys, please recommend the best advent calendar this year, I want a mix of skincare and makeup with a variety of brands.', FALSE),
  (2, 1, 'Best LED masks for anti-age?', 'I'm in the market for a new LED mask, I'm 34 with combo skin, currently looking into the DDG one, please share your recommendations.', FALSE),
  (3, 3, 'Tretinoin side effects', 'I've just started tretinoin, I'm on week 2 but my skin started peeling, is this normal?', FALSE),
  (4, 4, 'Number one eye cream', 'Hi group, can you please share your number one eye cream, I'm in the market for one that will hide my undereye bags and fine lines.', FALSE),
  (5, 4, 'European SPF', 'Hi group, I'm going on a trip to Europe in two weeks and I want to get a hold of great SPF I can't get in the States, please give me your best ones!', TRUE);
  


INSERT INTO `replies` (reply_id, topic_id, author_id, content)
VALUES
  (1, 1, 2, 'The SpaceNK one is just as great as previous years!'),
  (2, 2, 1, 'Quite happy with the Shark one, it was recommended by Caroline Hirons, too.'),
  (3, 1, 3, 'I got the Harrods one and it's really nice.'),
  (4, 3, 4, 'How often are you using tret? Did you start with sandwich method?'),
  (5, 4, 2, 'The AOS one is really good.'),
  (6, 2, 6, 'I use the Omnilux and am quite happy with the results.'),
  (7, 2, 3, 'Currently using CurrentBody 2, it's shown tremendous results with my collagen production.),
  (8, 1, 4, 'Lookfantastic is great value for money, and their beauty chest too.'),
  (9, 4, 3, 'I don't believe eye cream is necessary, it's just moisturizer for your eyes.'),
  (10, 1, 5, 'Did you see the SKIMS one? She's having a laugh!'),
  (11, 3, 3, 'Tretinoin isn't really good for everyone, perhaps you might want to try over-the-counter retinal instead.'),
  (12, 2, 3, '+ for Shark, been using it since last year.'),
  (13, 5, 2, 'Have you tried any Korean SPF, they're on par with the European ones.),
  (14, 5, 1, 'No, European are far superior than Korean and US-based SPF. The Australian are the best ones though.'),
  (15, 4, 1, 'Quite happy with Autocorrect, it has a pearly finish and giving that instant gratification xxx),
  (16, 5, 3, 'Of course the best one is LRP Anthelios UVMune 400 but make sure you're getting the European version, it's not the same as in the States.'),
  (17, 4, 2, 'Really really enjoy the Medik8 Eyelift Peptides.');
  


INSERT INTO `reply_votes` (user_id, reply_id, vote)
VALUES 
  (1, 1, 1),
  (2, 3, -1),
  (3, 2, 1),
  (4, 1, 1);


-- best replies are voted by the author of the topic
INSERT INTO `best_replies` (topic_id, reply_id)
VALUES
  (1, 3),
  (2, 2);


-- test the private topic members
INSERT INTO `topic_members` (topic_id, user_id) VALUES
  (5, 3),
  (5, 2);

