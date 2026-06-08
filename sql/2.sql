-- ============================================================
-- 02_migrate_data_fixed_v2.sql
-- Перенос данных с отключением ограничений и исправлением несоответствий
-- ============================================================

USE ScoobyQuestDB_V2;
GO

-- ------------------------------------------------------------------
-- 0. Отключение всех ограничений FOREIGN KEY и CHECK
-- ------------------------------------------------------------------
DECLARE @sql NVARCHAR(MAX) = '';
SELECT @sql = @sql + 'ALTER TABLE ' + QUOTENAME(OBJECT_SCHEMA_NAME(parent_object_id)) + '.' + QUOTENAME(OBJECT_NAME(parent_object_id)) + ' NOCHECK CONSTRAINT ' + QUOTENAME(name) + ';' + CHAR(13)
FROM sys.foreign_keys;
EXEC sp_executesql @sql;

SET @sql = '';
SELECT @sql = @sql + 'ALTER TABLE ' + QUOTENAME(OBJECT_SCHEMA_NAME(parent_object_id)) + '.' + QUOTENAME(OBJECT_NAME(parent_object_id)) + ' NOCHECK CONSTRAINT ' + QUOTENAME(name) + ';' + CHAR(13)
FROM sys.check_constraints;
EXEC sp_executesql @sql;
GO

-- ------------------------------------------------------------------
-- 1. Пользователи (корректируем avatar_id)
-- ------------------------------------------------------------------
SET IDENTITY_INSERT Users ON;
INSERT INTO Users (id, username, password_hash, role, full_name, group_name, avatar_id, created_at, parent_email)
SELECT 
    id, username, password_hash, role, full_name, group_name, 
    CASE WHEN avatar_id BETWEEN 0 AND 4 THEN avatar_id ELSE 0 END, 
    created_at, parent_email
FROM ScoobyQuestDB.dbo.Users;
SET IDENTITY_INSERT Users OFF;

-- ------------------------------------------------------------------
-- 2. Группы
-- ------------------------------------------------------------------
SET IDENTITY_INSERT Groups ON;
INSERT INTO Groups (id, group_name, age_category, current_quest_id, teacher_id, is_active, created_date)
SELECT id, group_name, age_category, current_quest_id, teacher_id, is_active, created_date
FROM ScoobyQuestDB.dbo.Groups;
SET IDENTITY_INSERT Groups OFF;

-- ------------------------------------------------------------------
-- 3. Квесты
-- ------------------------------------------------------------------
SET IDENTITY_INSERT Quests ON;
INSERT INTO Quests (id, quest_name, age_category, description, duration_days, is_active)
SELECT id, quest_name, age_category, description, duration_days, is_active
FROM ScoobyQuestDB.dbo.Quests;
SET IDENTITY_INSERT Quests OFF;

-- ------------------------------------------------------------------
-- 4. Этапы квестов
-- ------------------------------------------------------------------
SET IDENTITY_INSERT QuestStages ON;
INSERT INTO QuestStages (id, quest_id, stage_number, stage_name, description, educational_goal, max_score, required_time_min)
SELECT id, quest_id, stage_number, stage_name, description, educational_goal, max_score, required_time_min
FROM ScoobyQuestDB.dbo.QuestStages;
SET IDENTITY_INSERT QuestStages OFF;

-- ------------------------------------------------------------------
-- 5. Локации
-- ------------------------------------------------------------------
SET IDENTITY_INSERT Locations ON;
INSERT INTO Locations (id, quest_id, location_number, location_name, background_image, description, music)
SELECT id, quest_id, location_number, location_name, background_image, description, NULL
FROM ScoobyQuestDB.dbo.Locations;
SET IDENTITY_INSERT Locations OFF;

-- ------------------------------------------------------------------
-- 6. Задания (без dialogue_id)
-- ------------------------------------------------------------------
SET IDENTITY_INSERT Tasks ON;
INSERT INTO Tasks (id, location_id, task_type, difficulty, question_text, correct_answer, options, hint_text, max_score, time_limit)
SELECT id, location_id, task_type, difficulty, question_text, correct_answer, options, hint_text, max_score, time_limit
FROM ScoobyQuestDB.dbo.Tasks;
SET IDENTITY_INSERT Tasks OFF;

-- ------------------------------------------------------------------
-- 7. Прогресс детей (конвертируем completed_stages -> completed_minigames)
-- ------------------------------------------------------------------
INSERT INTO ChildProgress (child_id, quest_id, current_stage, completed_minigames, total_stages, score, last_activity, status)
SELECT 
    cp.child_id,
    cp.quest_id,
    cp.current_stage,
    CASE 
        WHEN cp.completed_stages > 0 THEN 
            'S-' + (
                SELECT STRING_AGG(CAST(n AS VARCHAR), '-') 
                FROM (SELECT TOP (cp.completed_stages) ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS n 
                      FROM master.dbo.spt_values) AS numbers
            )
        ELSE NULL
    END,
    cp.total_stages,
    cp.score,
    cp.last_activity,
    cp.status
FROM ScoobyQuestDB.dbo.ChildProgress cp;

-- ------------------------------------------------------------------
-- 8. Достижения (фильтруем только допустимые типы)
-- ------------------------------------------------------------------
SET IDENTITY_INSERT Achievements ON;
INSERT INTO Achievements (id, child_id, achievement_type, achievement_name, awarded_date, quest_id, stage_id)
SELECT 
    id, child_id, 
    CASE 
        WHEN achievement_type IN ('clue', 'toy', 'quest_complete') THEN achievement_type
        ELSE 'quest_complete'
    END,
    achievement_name, awarded_date, quest_id, stage_id
FROM ScoobyQuestDB.dbo.Achievements
WHERE achievement_type IN ('clue', 'toy', 'quest_complete');
SET IDENTITY_INSERT Achievements OFF;

-- ------------------------------------------------------------------
-- 9. Ответы детей (только те, где child_id существует в Users)
-- ------------------------------------------------------------------
SET IDENTITY_INSERT ChildAnswers ON;
INSERT INTO ChildAnswers (id, child_id, task_id, answer, score, completion_time, completed_at)
SELECT ca.id, ca.child_id, ca.task_id, ca.answer, ca.score, ca.completion_time, ca.completed_at
FROM ScoobyQuestDB.dbo.ChildAnswers ca
WHERE EXISTS (SELECT 1 FROM Users u WHERE u.id = ca.child_id);
SET IDENTITY_INSERT ChildAnswers OFF;

-- ------------------------------------------------------------------
-- 10. Системные настройки
-- ------------------------------------------------------------------
INSERT INTO SystemSettings (setting_key, setting_value, description)
SELECT setting_key, setting_value, description
FROM ScoobyQuestDB.dbo.SystemSettings;

-- ------------------------------------------------------------------
-- 11. Логи системы (только где user_id существует)
-- ------------------------------------------------------------------
SET IDENTITY_INSERT SystemLogs ON;
INSERT INTO SystemLogs (id, user_id, action_type, description, ip_address, log_date)
SELECT sl.id, sl.user_id, sl.action_type, sl.description, sl.ip_address, sl.log_date
FROM ScoobyQuestDB.dbo.SystemLogs sl
WHERE sl.user_id IS NULL OR EXISTS (SELECT 1 FROM Users u WHERE u.id = sl.user_id);
SET IDENTITY_INSERT SystemLogs OFF;

-- ------------------------------------------------------------------
-- 12. EmailTemplates (если есть)
-- ------------------------------------------------------------------
SET IDENTITY_INSERT EmailTemplates ON;
INSERT INTO EmailTemplates (id, template_name, subject, body_text, is_active, last_modified)
SELECT id, template_name, subject, body_text, is_active, last_modified
FROM ScoobyQuestDB.dbo.EmailTemplates;
SET IDENTITY_INSERT EmailTemplates OFF;

-- ------------------------------------------------------------------
-- 13. Включение всех ограничений обратно (с объявлением переменной)
-- ------------------------------------------------------------------
DECLARE @sql_enable NVARCHAR(MAX) = '';
SELECT @sql_enable = @sql_enable + 'ALTER TABLE ' + QUOTENAME(OBJECT_SCHEMA_NAME(parent_object_id)) + '.' + QUOTENAME(OBJECT_NAME(parent_object_id)) + ' CHECK CONSTRAINT ' + QUOTENAME(name) + ';' + CHAR(13)
FROM sys.foreign_keys;
EXEC sp_executesql @sql_enable;
SET @sql_enable = '';
SELECT @sql_enable = @sql_enable + 'ALTER TABLE ' + QUOTENAME(OBJECT_SCHEMA_NAME(parent_object_id)) + '.' + QUOTENAME(OBJECT_NAME(parent_object_id)) + ' CHECK CONSTRAINT ' + QUOTENAME(name) + ';' + CHAR(13)
FROM sys.check_constraints;
EXEC sp_executesql @sql_enable;
GO

PRINT 'Перенос данных завершён успешно.';
GO