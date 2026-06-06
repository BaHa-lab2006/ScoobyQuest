from game_wrappers import ScoobyGameWrapper, LibraryGhostGameWrapper, GhostGameWrapper
from database import db_manager

def get_game_for_child(screen, user_info):
    """
    Определяет игру по актуальному квесту группы ребёнка.
    user_info должен содержать хотя бы 'group_name'.
    """
    group_name = user_info.get('group_name')
    if not group_name:
        # fallback: если нет группы, выбираем квест по умолчанию (демо)
        return ScoobyGameWrapper(screen, user_info)

    quest_id = db_manager.get_group_current_quest_id(group_name)
    
    # Маппинг quest_id → класс игры
    # (предполагаем, что id квестов: 1 - Scooby, 2 - LibraryGhost, 3 - Ghost)
    game_by_quest = {
        1: ScoobyGameWrapper,
        2: LibraryGhostGameWrapper,
        3: GhostGameWrapper,
    }
    
    game_cls = game_by_quest.get(quest_id, ScoobyGameWrapper)
    return game_cls(screen, user_info)