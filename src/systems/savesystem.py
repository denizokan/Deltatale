import os
import json

class SaveSystem:
    def __init__(self):
        self.save_dir = "./data"
        if not os.path.exists(self.save_dir):
            try:
                os.mkdir(self.save_dir)
                print("Data folder created.")
            except Exception as e:
                print(f"An error has occured while trying to create save file directory: {e}")
    
    def get_save_path(self, slot_index):
        """Returns the file path of a save file with index."""
        return os.path.join(self.save_dir, f"save_{slot_index}.json")
    
    def save_file(self, slot_index, data):
        """Dumps the memory into a save file with slot index."""
        file_path = self.get_save_path(slot_index)
        with open(file_path, "w") as file:
            json.dump(data, file, indent=4)
    
    def exists(self, slot_index):
        return os.path.exists(self.get_save_path(slot_index))

    def load_file(self, slot_index):
        """Reads and returns a save file with slot index. If the file with slot index does not exist, returns an empty save slot."""
        file_path = self.get_save_path(slot_index)
        try:
            with open(file_path, "r") as file:
                data = json.load(file)
                return data
        except FileNotFoundError:
            data = {
                "name": "[EMPTY]",
                "location": "--------",
                "playtime": "0",
                "isEmpty": True
            }
            return data
        except Exception as e:
            raise RuntimeError(f"Save file {slot_index} is corrupted or inaccessible.") from e