-- ============================================================
-- 01_create_new_db.sql
-- Создаёт новую БД ScoobyQuestDB_V2 со структурой из database.sql
-- ============================================================

USE master;
GO

IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'ScoobyQuestDB_V2')
BEGIN
    CREATE DATABASE ScoobyQuestDB_V2;
END
GO

USE ScoobyQuestDB_V2;
GO

-- ============================================================
-- Таблицы без зависимостей
-- ============================================================

CREATE TABLE Quests (
    id INT IDENTITY(1,1) PRIMARY KEY,
    quest_name NVARCHAR(100) NOT NULL,
    age_category NVARCHAR(20) NOT NULL CHECK (age_category IN ('4-5', '5-6', '6-7')),
    description NVARCHAR(500),
    duration_days INT,
    is_active BIT NOT NULL DEFAULT 1
);

CREATE TABLE Assets (
    id INT IDENTITY(1,1) PRIMARY KEY,
    asset_key NVARCHAR(100) NOT NULL UNIQUE,
    asset_type NVARCHAR(30) NOT NULL CHECK (asset_type IN ('image', 'sound', 'voice', 'music')),
    file_path NVARCHAR(500) NOT NULL,
    description NVARCHAR(200)
);

CREATE TABLE Users (
    id INT IDENTITY(1,1) PRIMARY KEY,
    username NVARCHAR(50) NOT NULL UNIQUE,
    password_hash NVARCHAR(255) NOT NULL,
    role NVARCHAR(20) NOT NULL CHECK (role IN ('admin', 'teacher', 'child')),
    full_name NVARCHAR(100) NOT NULL,
    group_name NVARCHAR(50) NULL,
    avatar_id INT NOT NULL DEFAULT 0 CHECK (avatar_id BETWEEN 0 AND 4),
    created_at DATETIME NOT NULL DEFAULT GETDATE(),
    parent_email NVARCHAR(255) NULL
);

CREATE TABLE SystemSettings (
    id INT IDENTITY(1,1) PRIMARY KEY,
    setting_key NVARCHAR(50) NOT NULL UNIQUE,
    setting_value NVARCHAR(MAX),
    description NVARCHAR(200)
);

CREATE TABLE EmailTemplates (
    id INT IDENTITY(1,1) PRIMARY KEY,
    template_name NVARCHAR(50) NOT NULL UNIQUE,
    subject NVARCHAR(200) NOT NULL,
    body_text NVARCHAR(MAX) NOT NULL,
    is_active BIT NOT NULL DEFAULT 1,
    last_modified DATETIME NOT NULL DEFAULT GETDATE()
);

-- ============================================================
-- Таблицы с зависимостями от Users, Quests
-- ============================================================

CREATE TABLE Groups (
    id INT IDENTITY(1,1) PRIMARY KEY,
    group_name NVARCHAR(50) NOT NULL UNIQUE,
    age_category NVARCHAR(20) NOT NULL CHECK (age_category IN ('4-5', '5-6', '6-7')),
    current_quest_id INT NULL,
    teacher_id INT NULL,
    is_active BIT NOT NULL DEFAULT 1,
    created_date DATE NOT NULL DEFAULT GETDATE(),
    CONSTRAINT FK_Groups_Quests FOREIGN KEY (current_quest_id) REFERENCES Quests(id),
    CONSTRAINT FK_Groups_Users FOREIGN KEY (teacher_id) REFERENCES Users(id)
);

ALTER TABLE Users ADD CONSTRAINT FK_Users_Groups FOREIGN KEY (group_name) REFERENCES Groups(group_name);

CREATE TABLE QuestStages (
    id INT IDENTITY(1,1) PRIMARY KEY,
    quest_id INT NOT NULL,
    stage_number INT NOT NULL,
    stage_name NVARCHAR(100) NOT NULL,
    description NVARCHAR(500),
    educational_goal NVARCHAR(300),
    max_score INT NOT NULL DEFAULT 10,
    required_time_min INT,
    CONSTRAINT FK_QuestStages_Quests FOREIGN KEY (quest_id) REFERENCES Quests(id)
);

CREATE TABLE Locations (
    id INT IDENTITY(1,1) PRIMARY KEY,
    quest_id INT NOT NULL,
    location_number INT NOT NULL,
    location_name NVARCHAR(100) NOT NULL,
    background_image NVARCHAR(200),
    description NVARCHAR(300),
    music NVARCHAR(200),
    CONSTRAINT FK_Locations_Quests FOREIGN KEY (quest_id) REFERENCES Quests(id)
);

CREATE TABLE Dialogues (
    id INT IDENTITY(1,1) PRIMARY KEY,
    dialogue_name NVARCHAR(100) NOT NULL UNIQUE,
    quest_id INT NULL,
    location_id INT NULL,
    CONSTRAINT FK_Dialogues_Quests FOREIGN KEY (quest_id) REFERENCES Quests(id),
    CONSTRAINT FK_Dialogues_Locations FOREIGN KEY (location_id) REFERENCES Locations(id)
);
CREATE TABLE Tasks (
    id INT IDENTITY(1,1) PRIMARY KEY,
    location_id INT NOT NULL,
    task_type NVARCHAR(30) NOT NULL CHECK (task_type IN ('logic', 'math', 'memory', 'puzzle', 'creative', 'secret')),
    difficulty INT NOT NULL CHECK (difficulty BETWEEN 1 AND 3),
    question_text NVARCHAR(500),
    correct_answer NVARCHAR(200),
    options NVARCHAR(MAX),
    hint_text NVARCHAR(300),
    max_score INT NOT NULL DEFAULT 10,
    time_limit INT NOT NULL DEFAULT 0,
    dialogue_id INT NULL,
    CONSTRAINT FK_Tasks_Locations FOREIGN KEY (location_id) REFERENCES Locations(id),
    CONSTRAINT FK_Tasks_Dialogues FOREIGN KEY (dialogue_id) REFERENCES Dialogues(id)
);

CREATE TABLE LocationZones (
    id INT IDENTITY(1,1) PRIMARY KEY,
    location_id INT NOT NULL,
    zone_name NVARCHAR(50) NOT NULL,
    zone_type NVARCHAR(30) NOT NULL CHECK (zone_type IN ('door', 'minigame', 'secret', 'dialog')),
    rect_x INT NOT NULL,
    rect_y INT NOT NULL,
    rect_width INT NOT NULL,
    rect_height INT NOT NULL,
    target_id INT NULL,
    needs_complete BIT NOT NULL DEFAULT 0,
    order_index INT NOT NULL DEFAULT 0,
    CONSTRAINT FK_LocationZones_Locations FOREIGN KEY (location_id) REFERENCES Locations(id)
);

CREATE TABLE DialogueLines (
    id INT IDENTITY(1,1) PRIMARY KEY,
    dialogue_id INT NOT NULL,
    line_order INT NOT NULL,
    character_name NVARCHAR(50) NOT NULL,
    text NVARCHAR(500) NOT NULL,
    voice_asset_key NVARCHAR(100) NULL,
    CONSTRAINT FK_DialogueLines_Dialogues FOREIGN KEY (dialogue_id) REFERENCES Dialogues(id),
    CONSTRAINT FK_DialogueLines_Assets FOREIGN KEY (voice_asset_key) REFERENCES Assets(asset_key)
);

CREATE TABLE AssetBindings (
    id INT IDENTITY(1,1) PRIMARY KEY,
    entity_type NVARCHAR(50) NOT NULL,
    entity_id INT NOT NULL,
    asset_id INT NOT NULL,
    role NVARCHAR(50) NOT NULL,
    CONSTRAINT FK_AssetBindings_Assets FOREIGN KEY (asset_id) REFERENCES Assets(id)
);

CREATE TABLE ChildProgress (
    id INT IDENTITY(1,1) PRIMARY KEY,
    child_id INT NOT NULL,
    quest_id INT NOT NULL,
    current_stage INT NOT NULL DEFAULT 1,
    completed_minigames NVARCHAR(100) NULL,
    total_stages INT NOT NULL,
    score DECIMAL(5,2) NOT NULL DEFAULT 0,
    last_activity DATETIME NULL,
    status NVARCHAR(20) NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'paused', 'completed', 'archived')),
    CONSTRAINT FK_ChildProgress_Users FOREIGN KEY (child_id) REFERENCES Users(id),
    CONSTRAINT FK_ChildProgress_Quests FOREIGN KEY (quest_id) REFERENCES Quests(id)
);

CREATE TABLE ChildAnswers (
    id INT IDENTITY(1,1) PRIMARY KEY,
    child_id INT NOT NULL,
    task_id INT NOT NULL,
    answer NVARCHAR(MAX),
    score DECIMAL(5,2),
    completion_time INT,
    completed_at DATETIME NOT NULL DEFAULT GETDATE(),
    CONSTRAINT FK_ChildAnswers_Users FOREIGN KEY (child_id) REFERENCES Users(id),
    CONSTRAINT FK_ChildAnswers_Tasks FOREIGN KEY (task_id) REFERENCES Tasks(id)
);

CREATE TABLE Achievements (
    id INT IDENTITY(1,1) PRIMARY KEY,
    child_id INT NOT NULL,
    achievement_type NVARCHAR(50) NOT NULL
        CHECK (achievement_type IN ('clue', 'toy', 'quest_complete')),
    achievement_name NVARCHAR(100) NOT NULL,
    awarded_date DATETIME NOT NULL DEFAULT GETDATE(),
    quest_id INT NULL,
    stage_id INT NULL,
    CONSTRAINT FK_Achievements_Users FOREIGN KEY (child_id) REFERENCES Users(id),
    CONSTRAINT FK_Achievements_Quests FOREIGN KEY (quest_id) REFERENCES Quests(id),
    CONSTRAINT FK_Achievements_QuestStages FOREIGN KEY (stage_id) REFERENCES QuestStages(id)
);
CREATE TABLE ParentNotifications (
    id INT IDENTITY(1,1) PRIMARY KEY,
    child_id INT NOT NULL,
    notification_type NVARCHAR(50) NOT NULL
        CHECK (notification_type IN ('progress', 'achievement', 'reminder', 'custom')),
    message NVARCHAR(500) NOT NULL,
    sent_date DATETIME NULL,
    sent_via NVARCHAR(20) NULL CHECK (sent_via IN ('email')),
    status NVARCHAR(20) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'sent', 'failed')),
    CONSTRAINT FK_ParentNotifications_Users FOREIGN KEY (child_id) REFERENCES Users(id)
);

CREATE TABLE SystemLogs (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NULL,
    action_type NVARCHAR(50) NOT NULL,
    description NVARCHAR(500),
    ip_address NVARCHAR(50),
    log_date DATETIME NOT NULL DEFAULT GETDATE(),
    CONSTRAINT FK_SystemLogs_Users FOREIGN KEY (user_id) REFERENCES Users(id)
);

CREATE TABLE QuestHistory (
    id INT IDENTITY(1,1) PRIMARY KEY,
    group_id INT NOT NULL,
    quest_id INT NOT NULL,
    completion_date DATE NOT NULL,
    avg_score DECIMAL(5,2),
    archived BIT NOT NULL DEFAULT 0,
    CONSTRAINT FK_QuestHistory_Groups FOREIGN KEY (group_id) REFERENCES Groups(id),
    CONSTRAINT FK_QuestHistory_Quests FOREIGN KEY (quest_id) REFERENCES Quests(id)
);

CREATE TABLE Schedule (
    id INT IDENTITY(1,1) PRIMARY KEY,
    group_id INT NOT NULL,
    quest_id INT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    is_active BIT NOT NULL DEFAULT 1,
    early_access BIT NOT NULL DEFAULT 0,
    late_access BIT NOT NULL DEFAULT 0,
    CONSTRAINT FK_Schedule_Groups FOREIGN KEY (group_id) REFERENCES Groups(id),
    CONSTRAINT FK_Schedule_Quests FOREIGN KEY (quest_id) REFERENCES Quests(id)
);

USE ScoobyQuestDB_V2;
CREATE USER Shagy FOR LOGIN Shagy;
EXEC sp_addrolemember 'db_owner', 'Shagy';

PRINT 'База данных ScoobyQuestDB_V2 успешно создана.';
GO