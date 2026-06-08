-- ============================================================
-- 03_insert_reference_data_final.sql
-- Добавляет только отсутствующие справочные данные, без дубликатов asset_key
-- ============================================================

USE ScoobyQuestDB_V2;
GO

-- ------------------------------------------------------------------
-- 1. Квесты
-- ------------------------------------------------------------------
SET IDENTITY_INSERT Quests ON;
INSERT INTO Quests (id, quest_name, age_category, description, duration_days, is_active)
SELECT id, quest_name, age_category, description, duration_days, is_active
FROM (VALUES 
    (1, 'Тайна пропавших игрушек', '4-5', 'В детском саду пропадают игрушки. Помогите Скуби и команде найти виновника!', 14, 1),
    (2, 'Тайна Призрака в Консервном Замке', '5-6', 'На заводе происходят странные события. Раскройте тайну призрака, используя логику и математику.', 14, 1),
    (3, 'Дело о Призраке Библиотеки', '6-7', 'В библиотеке летают книги и появляются загадочные следы. Соберите слово и раскройте секрет.', 14, 1)
) AS src(id, quest_name, age_category, description, duration_days, is_active)
WHERE NOT EXISTS (SELECT 1 FROM Quests WHERE Quests.id = src.id);
SET IDENTITY_INSERT Quests OFF;

-- ------------------------------------------------------------------
-- 2. Этапы квестов
-- ------------------------------------------------------------------
SET IDENTITY_INSERT QuestStages ON;
INSERT INTO QuestStages (id, quest_id, stage_number, stage_name, description, educational_goal, max_score, required_time_min)
SELECT id, quest_id, stage_number, stage_name, description, educational_goal, max_score, required_time_min
FROM (VALUES
(1, 1, 1, 'Игровая комната', 'Найди первую улику и игрушку, сортируя кубики.', 'Сортировка по цвету, развитие логики', 10, 10),
(2, 1, 2, 'Спальня', 'Соедини тапочки в пары и определи эмоцию.', 'Внимание, парные предметы, эмпатия', 10, 12),
(3, 1, 3, 'Столовая', 'Сосчитай ложки и прочитай испачканную записку.', 'Счёт до 5, мелкая моторика', 10, 10),
(4, 1, 4, 'Музыкальный зал', 'Повтори ритм на бубнах и собери пазл.', 'Ритм, пространственное мышление', 10, 15),
(5, 1, 5, 'Кабинет заведующей', 'Сопоставь улики на фото сторожа и раскрой дело.', 'Анализ, дедукция', 10, 10),
(6, 2, 1, 'Вход на завод', 'Найди отличия в планах здания.', 'Внимание, наблюдательность', 10, 8),
(7, 2, 2, 'Склад', 'Сосчитай упавшие банки.', 'Счёт до 10', 10, 5),
(8, 2, 3, 'Лаборатория', 'Реши примеры на сложение.', 'Математика в пределах 5', 10, 7),
(9, 2, 4, 'Конвейер', 'Продолжи логический ряд с банками.', 'Логические ряды, паттерны', 10, 6),
(10, 2, 5, 'Офис', 'Распредели предметы на съедобные/несъедобные.', 'Классификация', 10, 8),
(11, 2, 6, 'Крыша', 'Собери пазл из деталей конвейера.', 'Конструктивное мышление', 10, 10),
(12, 3, 1, 'Читальный зал', 'Расставь книги по порядку и определи логический ряд.', 'Порядковый счёт, логика', 10, 10),
(13, 3, 2, 'Детский абонемент', 'Составь число 7 из предметов и найди пару букв.', 'Состав числа, память', 10, 12),
(14, 3, 3, 'Книгохранилище', 'Поставь правильное время на часах и проведи стеллаж по лабиринту.', 'Время, пространство', 10, 15),
(15, 3, 4, 'Кабинет', 'Собери след лапы и определи причину-следствие.', 'Логика', 10, 10),
(16, 3, 5, 'Подвал', 'Разгадай ребус и выбери чётные числа до 20.', 'Шифровка, чётность', 10, 12),
(17, 3, 6, 'Чердак', 'Пройди финальную викторину и собери слово ВОРОНА.', 'Обобщение, выводы', 10, 15)
) AS src(id, quest_id, stage_number, stage_name, description, educational_goal, max_score, required_time_min)
WHERE NOT EXISTS (SELECT 1 FROM QuestStages WHERE QuestStages.id = src.id);
SET IDENTITY_INSERT QuestStages OFF;

-- ------------------------------------------------------------------
-- 3. Локации
-- ------------------------------------------------------------------
SET IDENTITY_INSERT Locations ON;
INSERT INTO Locations (id, quest_id, location_number, location_name, background_image, description, music)
SELECT id, quest_id, location_number, location_name, background_image, description, music
FROM (VALUES
(1, 1, 1, 'Игровая комната', 'game_room_bg', 'Разбросанные кубики и корзины.', NULL),
(2, 1, 2, 'Спальня', 'bedroom_bg', 'Тихая комната с кроватками и тапочками.', NULL),
(3, 1, 3, 'Столовая', 'canteen_bg', 'Накрытый стол и грязная записка.', NULL),
(4, 1, 4, 'Музыкальный зал', 'music_hall_bg', 'Бубны и пазл на стене.', NULL),
(5, 1, 5, 'Кабинет заведующей', 'office_bg', 'Фотография сторожа на столе.', NULL),
(6, 2, 1, 'Вход на завод', 'entrance.png', 'План здания с отличиями.', NULL),
(7, 2, 2, 'Склад', 'warehouse.png', 'Банки, упавшие с полки.', NULL),
(8, 2, 3, 'Лаборатория', 'lab.png', 'Пробирки и примеры.', NULL),
(9, 2, 4, 'Конвейер', 'conveyor.png', 'Движущаяся лента с банками.', NULL),
(10, 2, 5, 'Офис', 'office.png', 'Стол с бумагами.', NULL),
(11, 2, 6, 'Крыша', 'roof.png', 'Панорама завода, детали пазла.', NULL),
(12, 3, 1, 'Читальный зал', 'reading_hall_bg', 'Стеллажи с книгами.', NULL),
(13, 3, 2, 'Детский абонемент', 'kids_section_bg', 'Яркие полки и игрушки.', NULL),
(14, 3, 3, 'Книгохранилище', 'book_storage_bg', 'Высокие стеллажи, часы.', NULL),
(15, 3, 4, 'Кабинет', 'office_bg', 'Письменный стол, пазл следа.', NULL),
(16, 3, 5, 'Подвал', 'basement_bg', 'Тёмное помещение с ребусами.', NULL),
(17, 3, 6, 'Чердак', 'attic_bg', 'Старые вещи, финальная викторина.', NULL)
) AS src(id, quest_id, location_number, location_name, background_image, description, music)
WHERE NOT EXISTS (SELECT 1 FROM Locations WHERE Locations.id = src.id);
SET IDENTITY_INSERT Locations OFF;

-- ------------------------------------------------------------------
-- 4. Задания
-- ------------------------------------------------------------------
SET IDENTITY_INSERT Tasks ON;
INSERT INTO Tasks (id, location_id, task_type, difficulty, question_text, correct_answer, options, hint_text, max_score, time_limit)
SELECT id, location_id, task_type, difficulty, question_text, correct_answer, options, hint_text, max_score, time_limit
FROM (VALUES
(1, 1, 'logic', 1, 'Разложи кубики по цветам в соответствующие корзины.', NULL, NULL, 'Каждый кубик должен попасть в корзину того же цвета.', 10, 0),
(2, 1, 'creative', 2, 'Найди 5 отличий на картинках игровой комнаты.', NULL, NULL, 'Сравни обе картинки внимательно.', 10, 60),
(3, 2, 'logic', 1, 'Соедини тапочки одинакового размера в пары.', NULL, NULL, 'Большой с большим, маленький с маленьким.', 10, 0),
(4, 2, 'creative', 1, 'Какая эмоция подходит к ситуации: "Игрушкам стало грустно"?', 'sad', 'happy,sad,scared', 'Грусть – когда теряешь друга.', 10, 30),
(5, 3, 'math', 1, 'Положи по одной ложке на каждую тарелку (всего 5 тарелок).', NULL, NULL, 'Сосчитай тарелки и положи столько же ложек.', 10, 0),
(6, 3, 'secret', 2, 'Протри пятно, чтобы прочитать тайную записку.', NULL, NULL, 'Води мышкой по грязному месту.', 10, 0),
(7, 4, 'puzzle', 2, 'Повтори последовательность звуков на бубнах.', NULL, NULL, 'Запомни порядок, в котором звучат бубны.', 10, 0),
(8, 4, 'puzzle', 2, 'Собери пазл из четырёх частей.', NULL, NULL, 'Перетащи кусочки на рамку.', 10, 0),
(9, 5, 'secret', 2, 'Сопоставь улики с местами на фото сторожа.', NULL, NULL, 'Перетащи каждую улику на её тень на фотографии.', 10, 0),
(10, 6, 'creative', 1, 'Найди отличия на планах здания.', NULL, NULL, 'Сравни два плана и кликни на отличия.', 10, 60),
(11, 7, 'math', 1, 'Сосчитай, сколько банок упало на пол.', '7', '0,1,2,3,4,5,6,7,8,9,10', 'Посмотри на картинку внимательно.', 10, 30),
(12, 8, 'math', 2, 'Реши пример: 3 + 2 = ?', '5', '1,2,3,4,5,6', 'Сложи сначала три банки, потом две.', 10, 30),
(13, 9, 'logic', 2, 'Какой цвет будет следующим в ряду: красный, синий, красный, синий, ...?', 'red', 'red,blue,green,yellow', 'Цвета чередуются.', 10, 30),
(14, 10, 'logic', 1, 'Распредели предметы: съедобное – в миску, несъедобное – в мусор.', NULL, NULL, 'Помоги Скуби выбрать еду.', 10, 0),
(15, 11, 'puzzle', 2, 'Собери пазл: Мотор ? Лента ? Банка.', NULL, NULL, 'Поставь детали в правильном порядке.', 10, 0),
(16, 12, 'logic', 1, 'Расставь книги по порядку: 1, 2, 3.', NULL, NULL, 'Перетащи книги на полки по порядку.', 10, 0),
(17, 12, 'logic', 2, 'Какой предмет следующий в ряду: красная, синяя, красная ...?', 'синяя', 'красная,синяя,зелёная', 'Цвета чередуются.', 10, 30),
(18, 13, 'math', 2, 'Составь число 7 из двух групп предметов.', NULL, NULL, 'Перетащи группы одного предмета друг на друга, чтобы вместе было 7.', 10, 0),
(19, 13, 'memory', 1, 'Найди пару одинаковых букв (А и А).', NULL, NULL, 'Открывай карточки и запоминай.', 10, 0),
(20, 14, 'logic', 2, 'Поставь стрелки часов на 3:00.', '3:00', NULL, 'Перетащи часовую и минутную стрелки.', 10, 45),
(21, 14, 'puzzle', 2, 'Проведи стеллаж к выходу (золотая дверь).', NULL, NULL, 'Перетащи стеллаж по лабиринту.', 10, 0),
(22, 15, 'puzzle', 2, 'Собери пазл – след лапы.', NULL, NULL, 'Перетащи части пазла в рамку.', 10, 0),
(23, 15, 'logic', 2, 'Выбери правильное следствие: если открыто окно и идёт дождь, то на полу...', 'лужа', 'лужа,лампа,закрытая книга', 'Что намокает?', 10, 30),
(24, 16, 'creative', 2, 'Разгадай ребус по картинкам и составь слово.', 'КРОНА', NULL, 'Нажми на буквы на клавиатуре.', 10, 0),
(25, 16, 'math', 1, 'Нажми на все чётные числа от 1 до 20.', NULL, NULL, 'Чётные числа делятся на 2.', 10, 0),
(26, 17, 'creative', 2, 'Ответь на вопросы финальной викторины.', NULL, NULL, 'Выбери правильный ответ.', 10, 0)
) AS src(id, location_id, task_type, difficulty, question_text, correct_answer, options, hint_text, max_score, time_limit)
WHERE NOT EXISTS (SELECT 1 FROM Tasks WHERE Tasks.id = src.id);
SET IDENTITY_INSERT Tasks OFF;

-- ------------------------------------------------------------------
-- 5. Зоны на локациях
-- ------------------------------------------------------------------
INSERT INTO LocationZones (location_id, zone_name, zone_type, rect_x, rect_y, rect_width, rect_height, target_id, needs_complete, order_index)
SELECT location_id, zone_name, zone_type, rect_x, rect_y, rect_width, rect_height, target_id, needs_complete, order_index
FROM (VALUES
(1, 'Сортировка кубиков', 'minigame', 801, 270, 70, 100, 1, 0, 1),
(1, 'Найди отличия', 'minigame', 0, 730, 220, 70, 2, 0, 2),
(1, 'Дверь в спальню', 'door', 1050, 590, 150, 210, 2, 1, 3),
(2, 'Тапочки-пары', 'minigame', 930, 732, 269, 51, 3, 0, 1),
(2, 'Эмоции', 'minigame', 330, 712, 107, 85, 4, 0, 2),
(2, 'Дверь в столовую', 'door', 1050, 590, 150, 210, 3, 1, 3),
(3, 'Ложки на тарелки', 'minigame', 433, 518, 281, 35, 5, 0, 1),
(3, 'Чистка записки', 'minigame', 623, 216, 35, 57, 6, 0, 2),
(3, 'Дверь в муз. зал', 'door', 1050, 590, 150, 210, 4, 1, 3),
(4, 'Ритм на бубнах', 'minigame', 33, 545, 524, 236, 7, 0, 1),
(4, 'Пазл', 'minigame', 667, 1, 92, 43, 8, 0, 2),
(4, 'Дверь в кабинет', 'door', 1050, 590, 150, 210, 5, 1, 3),
(5, 'Улики сторожа', 'minigame', 100, 100, 500, 700, 9, 0, 1)
) AS src(location_id, zone_name, zone_type, rect_x, rect_y, rect_width, rect_height, target_id, needs_complete, order_index)
WHERE NOT EXISTS (
    SELECT 1 FROM LocationZones 
    WHERE location_id = src.location_id AND zone_name = src.zone_name
);

-- ------------------------------------------------------------------
-- 6. Ассеты (уникальные ключи, без дублей)
-- ------------------------------------------------------------------
INSERT INTO Assets (asset_key, asset_type, file_path, description)
SELECT asset_key, asset_type, file_path, description
FROM (VALUES
-- Фоны game1
('prologue_bg', 'image', 'assets/game1/images/backgrounds/prologue_bg.png', 'Фон пролога'),
('game_room_bg', 'image', 'assets/game1/images/backgrounds/game_room_bg.png', 'Игровая комната'),
('bedroom_bg', 'image', 'assets/game1/images/backgrounds/bedroom_bg.png', 'Спальня'),
('canteen_bg', 'image', 'assets/game1/images/backgrounds/canteen_bg.png', 'Столовая'),
('music_hall_bg', 'image', 'assets/game1/images/backgrounds/music_hall_bg.png', 'Музыкальный зал'),
('office_bg', 'image', 'assets/game1/images/backgrounds/office_bg.png', 'Кабинет'),
-- Персонажи game1 (изображения)
('velma_normal', 'image', 'assets/game1/images/characters/velma_normal.png', 'Велма обычная'),
('scooby_scared_img', 'image', 'assets/game1/images/characters/scooby_scared.png', 'Скуби испуганный (изображение)'),
('shaggy_normal', 'image', 'assets/game1/images/characters/shaggy_normal.png', 'Шэгги'),
('fred_normal', 'image', 'assets/game1/images/characters/fred_normal.png', 'Фред'),
('daphne_normal', 'image', 'assets/game1/images/characters/daphne_normal.png', 'Дафна'),
('guard_normal', 'image', 'assets/game1/images/characters/guard_normal.png', 'Сторож'),
-- Предметы game1
('red_cube', 'image', 'assets/game1/images/items/red_cube.png', 'Красный кубик'),
('blue_cube', 'image', 'assets/game1/images/items/blue_cube.png', 'Синий кубик'),
('yellow_cube', 'image', 'assets/game1/images/items/yellow_cube.png', 'Жёлтый кубик'),
('red_basket', 'image', 'assets/game1/images/items/red_basket.png', 'Красная корзина'),
('blue_basket', 'image', 'assets/game1/images/items/blue_basket.png', 'Синяя корзина'),
('yellow_basket', 'image', 'assets/game1/images/items/yellow_basket.png', 'Жёлтая корзина'),
('button_clue', 'image', 'assets/game1/images/items/button_clue.png', 'Улика – пуговица'),
('newspaper_clue', 'image', 'assets/game1/images/items/newspaper_clue.png', 'Улика – газета'),
('green_paint_clue', 'image', 'assets/game1/images/items/green_paint.png', 'Улика – зелёная краска'),
('screwdriver_clue', 'image', 'assets/game1/images/items/screwdriver.png', 'Улика – отвёртка'),
-- Игрушки
('duck_toy', 'image', 'assets/game1/images/toys/duck_toy.png', 'Уточка'),
('bunny_toy', 'image', 'assets/game1/images/toys/bunny_toy.png', 'Зайка'),
('car_toy', 'image', 'assets/game1/images/toys/car_toy.png', 'Машинка'),
('doll_toy', 'image', 'assets/game1/images/toys/doll_toy.png', 'Кукла'),
-- UI
('door', 'image', 'assets/game1/images/ui/door.png', 'Дверь'),
('door_active', 'image', 'assets/game1/images/ui/door_active.png', 'Активная дверь'),
('lupa', 'image', 'assets/game1/images/ui/lupa.png', 'Лупа'),
-- Мини-игры game1
('difference_img_a', 'image', 'assets/game1/images/minigames/difference_img_a.png', 'Картинка А для отличий'),
('difference_img_b', 'image', 'assets/game1/images/minigames/difference_img_b.png', 'Картинка Б для отличий'),
('big_slipper', 'image', 'assets/game1/images/minigames/big_slipper.png', 'Большой тапок'),
('small_slipper', 'image', 'assets/game1/images/minigames/small_slipper.png', 'Маленький тапок'),
('emotion_happy', 'image', 'assets/game1/images/minigames/emotion_happy.png', 'Счастливая эмоция'),
('emotion_sad', 'image', 'assets/game1/images/minigames/emotion_sad.png', 'Грустная эмоция'),
('emotion_scared', 'image', 'assets/game1/images/minigames/emotion_scared.png', 'Испуганная эмоция'),
('plate', 'image', 'assets/game1/images/minigames/plate.png', 'Тарелка'),
('spoon', 'image', 'assets/game1/images/minigames/spoon.png', 'Ложка'),
('dirty_note', 'image', 'assets/game1/images/minigames/dirty_note.png', 'Грязная записка'),
('clean_note', 'image', 'assets/game1/images/minigames/clean_note.png', 'Чистая записка'),
('tambourine_1', 'image', 'assets/game1/images/minigames/tambourine_1.png', 'Бубен 1'),
('tambourine_2', 'image', 'assets/game1/images/minigames/tambourine_2.png', 'Бубен 2'),
('tambourine_3', 'image', 'assets/game1/images/minigames/tambourine_3.png', 'Бубен 3'),
('puzzle_1', 'image', 'assets/game1/images/minigames/puzzle_1.png', 'Пазл часть 1'),
('puzzle_2', 'image', 'assets/game1/images/minigames/puzzle_2.png', 'Пазл часть 2'),
('puzzle_3', 'image', 'assets/game1/images/minigames/puzzle_3.png', 'Пазл часть 3'),
('puzzle_4', 'image', 'assets/game1/images/minigames/puzzle_4.png', 'Пазл часть 4'),
('puzzle_frame', 'image', 'assets/game1/images/minigames/puzzle_frame.png', 'Рамка пазла'),
-- Звуки game1
('click_sfx', 'sound', 'assets/game1/sounds/sfx/click.wav', 'Клик'),
('success_sfx', 'sound', 'assets/game1/sounds/sfx/success.wav', 'Успех'),
('error_sfx', 'sound', 'assets/game1/sounds/sfx/error.wav', 'Ошибка'),
('drag_start', 'sound', 'assets/game1/sounds/sfx/drag_start.wav', 'Начало перетаскивания'),
('drag_drop', 'sound', 'assets/game1/sounds/sfx/drag_drop.wav', 'Бросок'),
('sort_place', 'sound', 'assets/game1/sounds/sfx/sort_place.wav', 'Поместили в корзину'),
('difference_found', 'sound', 'assets/game1/sounds/sfx/difference_found.wav', 'Найдено отличие'),
('match_pair', 'sound', 'assets/game1/sounds/sfx/match_pair.mp3', 'Пара найдена'),
('emotion_correct', 'sound', 'assets/game1/sounds/sfx/emotion_correct.wav', 'Правильная эмоция'),
('spoon_place', 'sound', 'assets/game1/sounds/sfx/spoon_place.wav', 'Ложка на месте'),
('erase', 'sound', 'assets/game1/sounds/sfx/erase.wav', 'Стирание'),
('rhythm_correct', 'sound', 'assets/game1/sounds/sfx/rhythm_correct.wav', 'Ритм верный'),
('puzzle_place', 'sound', 'assets/game1/sounds/sfx/puzzle_place.wav', 'Кусочек пазла поставлен'),
('tambourine_sound_1', 'sound', 'assets/game1/sounds/sfx/tambourine_sound_1.wav', 'Звук бубна 1'),
('tambourine_sound_2', 'sound', 'assets/game1/sounds/sfx/tambourine_sound_2.wav', 'Звук бубна 2'),
('tambourine_sound_3', 'sound', 'assets/game1/sounds/sfx/tambourine_sound_3.wav', 'Звук бубна 3'),
('fanfare', 'sound', 'assets/game1/sounds/sfx/fanfare.mp3', 'Фанфары'),
('applause', 'sound', 'assets/game1/sounds/sfx/applause.wav', 'Аплодисменты'),
-- Голоса game1 (используем суффикс _voice, чтобы избежать конфликта с изображениями)
('velma_intro_1', 'voice', 'assets/game1/voices/velma/intro_1.wav', 'Велма – вступление'),
('velma_sort_success', 'voice', 'assets/game1/voices/velma/sort_success.wav', 'Велма – успех сортировки'),
('velma_diff_success', 'voice', 'assets/game1/voices/velma/differences_success.wav', 'Велма – отличия найдены'),
('scooby_scared_voice', 'voice', 'assets/game1/voices/scooby/scared.wav', 'Скуби – испуг (голос)'),
('scooby_happy_bark', 'voice', 'assets/game1/voices/scooby/happy_bark.wav', 'Скуби – радостный лай'),
('shaggy_bedroom', 'voice', 'assets/game1/voices/shaggy/bedroom_1.wav', 'Шэгги – спальня'),
('shaggy_success', 'voice', 'assets/game1/voices/shaggy/bedroom_success.wav', 'Шэгги – успех'),
('fred_music_hall', 'voice', 'assets/game1/voices/fred/music_hall_1.wav', 'Фред – муззал'),
('fred_rhythm_success', 'voice', 'assets/game1/voices/fred/rhythm_success.wav', 'Фред – ритм успешен'),
('daphne_canteen', 'voice', 'assets/game1/voices/daphne/canteen_1.wav', 'Дафна – столовая'),
('daphne_note_success', 'voice', 'assets/game1/voices/daphne/clean_note_success.wav', 'Дафна – записка прочитана'),
('guard_confession', 'voice', 'assets/game1/voices/guard/finale_confession.wav', 'Сторож – признание'),
('guard_explanation', 'voice', 'assets/game1/voices/guard/finale_explanation.wav', 'Сторож – объяснение'),
-- Ключевые ассеты game2
('factory_ambient', 'music', 'assets/game2/sounds/music/factory_ambient.wav', 'Фон завода'),
('map_background', 'image', 'assets/game2/images/ui/map_background.png', 'Карта завода'),
('balance_scale', 'image', 'assets/game2/images/minigames/balance_scale.png', 'Весы'),
('pattern_red_can', 'image', 'assets/game2/images/minigames/pattern_red_can.png', 'Красная банка'),
('count_cans', 'image', 'assets/game2/images/minigames/count_cans.png', 'Банки для счёта'),
('sort_bowl', 'image', 'assets/game2/images/minigames/sort_bowl.png', 'Миска'),
('sort_trash', 'image', 'assets/game2/images/minigames/sort_trash.png', 'Мусорка'),
('puzzle_motor', 'image', 'assets/game2/images/minigames/puzzle_motor.png', 'Мотор'),
('puzzle_belt', 'image', 'assets/game2/images/minigames/puzzle_belt.png', 'Лента'),
('puzzle_can', 'image', 'assets/game2/images/minigames/puzzle_can.png', 'Банка'),
('correct', 'sound', 'assets/game2/sounds/sfx/correct.wav', 'Правильно'),
('wrong', 'sound', 'assets/game2/sounds/sfx/wrong.wav', 'Неправильно'),
-- Ассеты game3 (без дублей с game1)
('prolog_bg_lib', 'image', 'assets/game3/images/backgrounds/prolog_bg.png', 'Фон пролога библиотеки'),
('map_bg_lib', 'image', 'assets/game3/images/backgrounds/map_bg.png', 'Карта библиотеки'),
('reading_hall_bg', 'image', 'assets/game3/images/backgrounds/reading_hall.png', 'Читальный зал'),
('clock_face_lib', 'image', 'assets/game3/images/items/clock/clock_face.png', 'Циферблат'),
('success_lib', 'sound', 'assets/game3/sounds/sfx/success.mp3', 'Успех (библиотека)'),
('fail_lib', 'sound', 'assets/game3/sounds/sfx/fail.wav', 'Провал'),
('background_music_lib', 'music', 'assets/game3/sounds/music/background_music.mp3', 'Фоновая музыка библиотеки')
) AS src(asset_key, asset_type, file_path, description)
WHERE NOT EXISTS (SELECT 1 FROM Assets WHERE Assets.asset_key = src.asset_key);

-- ------------------------------------------------------------------
-- 7. Диалоги (только новые)
-- ------------------------------------------------------------------
INSERT INTO Dialogues (dialogue_name, quest_id, location_id)
SELECT dialogue_name, quest_id, location_id
FROM (VALUES
('Prologue_1', 1, NULL),
('Location1_Enter', 1, 1),
('Location2_Enter', 1, 2),
('Location3_Enter', 1, 3),
('Location4_Enter', 1, 4),
('Finale', 1, 5)
) AS src(dialogue_name, quest_id, location_id)
WHERE NOT EXISTS (SELECT 1 FROM Dialogues WHERE Dialogues.dialogue_name = src.dialogue_name);

-- ------------------------------------------------------------------
-- 8. Реплики диалогов (с исправленными voice_asset_key)
-- ------------------------------------------------------------------
INSERT INTO DialogueLines (dialogue_id, line_order, character_name, text, voice_asset_key)
SELECT d.id, src.line_order, src.character_name, src.text, src.voice_asset_key
FROM (VALUES
('Prologue_1', 1, 'Велма', 'Ребята, к нам в детский сад "Радуга" пришла беда! Каждое утро игрушки исчезают из группы!', 'velma_intro_1'),
('Prologue_1', 2, 'Скуби', 'Ррр-ррябя?!', 'scooby_scared_voice'),
('Prologue_1', 3, 'Ночной сторож', 'Это Ворчащий Гномик! Он не любит, когда дети шумят, вот и забирает игрушки!', NULL),
('Prologue_1', 4, 'Фред', 'Но мы, "Тайна Инкорпорейтед", не верим в сказки! Помоги нам найти настоящую причину!', NULL),
('Prologue_1', 5, 'Дафна', 'Будь нашим глазами и ушами в садике! Вперёд!', NULL),
('Location1_Enter', 1, 'Велма', 'Смотри, какой беспорядок! Игрушки не просто потерялись – их кто-то унёс. Давай наведём порядок и поищем подсказки.', NULL),
('Location2_Enter', 1, 'Шэгги', 'Здесь так тихо... Жутковато! Я слышал, Гномик особенно любит брать игрушки отсюда!', NULL),
('Location2_Enter', 2, 'Скуби', '(кивает и облизывается от волнения)', NULL),
('Location3_Enter', 1, 'Дафна', 'Смотри, кто-то здесь перекусил ночью. И не просто так... Кажется, он оставил нам записку. Но она перепачкана кашей!', NULL),
('Location4_Enter', 1, 'Фред', 'По моим расчётам, все найденные улики ведут сюда! И смотри – на полу возле горшка с цветком тоже зелёная краска!', NULL),
('Finale', 1, 'Сторож', 'Ох, ребята, вы меня раскусили... Это был я. Но я не вор!', 'guard_confession'),
('Finale', 2, 'Велма', 'Всё сходится! Пуговица, краска, отвёртка, объявление...', NULL),
('Finale', 3, 'Сторож', 'Я чинил игрушки по ночам, а про Гномика придумал, чтобы не мешали.', 'guard_explanation')
) AS src(dialogue_name, line_order, character_name, text, voice_asset_key)
INNER JOIN Dialogues d ON d.dialogue_name = src.dialogue_name
WHERE NOT EXISTS (
    SELECT 1 FROM DialogueLines dl 
    WHERE dl.dialogue_id = d.id AND dl.line_order = src.line_order
);

PRINT 'Справочные данные добавлены (только новые записи, дубликаты исключены).';
GO