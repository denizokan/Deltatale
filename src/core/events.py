class EventBus:
    """
    Central Pub/Sub Event System.
    
    ===========================================================================
    Registered Event Keys & Expected Data Payloads:
    ===========================================================================
    
    DIALOGUE / UI:
    - "START_DIALOGUE" : dict 
        Payload: {
            "text": list, 
            "interaction_index": int, 
            "type": str, 
            "interactable": dict, 
            "actors": dict
        }
    - "SHOW_SAVE_SCREEN" : dict 
        Payload: {"interactable": dict}
    - "OPEN_MENU" : int -> page_index (e.g., 0)

    ROOM / WORLD:
    - "CHANGE_ROOM"     : str  -> target_room_id (e.g., "ruins_2")
    - "START_CUTSCENE"  : str  -> cutscene_id (e.g., "intro_fall")

    AUDIO:
    - "PLAY_SOUND" : str -> sound_name (e.g., "snd_power")
    - "PLAY_MUSIC" : str -> music_name (e.g., "mus_ruins")
    - "STOP_SFX"   : str | list -> sound_name OR [sound_name, fadeout_ms]
    """
    _subscribers = {}

    @classmethod
    def subscribe(cls, event_type, callback):
        """Tells the bus: 'When [event_type] happens, run [callback]'."""
        if event_type not in cls._subscribers:
            cls._subscribers[event_type] = []

        cls._subscribers[event_type].append(callback)


    @classmethod
    def emit(cls, event_type, data=None):
        """Tells the bus: 'This event happened. Tell everyone listening and give data.'"""
        if event_type in cls._subscribers:
            for callback in cls._subscribers[event_type]:
                callback(data)


    @classmethod
    def clear(cls):
        """Useful for resetting the game or changing states."""
        cls._subscribers.clear()