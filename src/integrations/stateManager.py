# THINGS THAT ARE PERMANENT/PER USER:
# Trello board id, canvas user id, canvas base url
#
# THINGS THAT ARE UPDATED ONCE A QUARTER:
# canvas term id, canvas current courses
#
# State will be like a dictionary. If you pass it a key and a method, it will return the key if it exists or create one using the provided method

import os, json
class StateManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(StateManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, state_file="state.json"):
        if not hasattr(self, "initialized"):  # Prevent reinitialization
            self.state_file = state_file
            self.state = self._load_state()
            self.initialized = True  # Mark as initialized to avoid reloading

    def getOrPut(self,key,value,args=[]):
        if key not in self.state.keys():
            self.put(key,value,args)
        return self.get(key)

    def get(self, key):
        if key in self.state.keys():
            return self.state[key]
        return None

    def put(self, key, value, args=[]):
        if callable(value):
            self.state[key] = value(*args)
        else:
            self.state[key] = value
        self.save_state()

    def is_jsonable(x):
        try:
            json.dumps(x)
            return True
        except (TypeError, OverflowError):
            return False

    def _load_state(self):
        """Loads the state from a file or initializes an empty state."""
        if os.path.exists(self.state_file):
            with open(self.state_file, "r") as f:
                return json.load(f)
        return {}

    def save_state(self):
        """Saves the current state to a file."""
        with open(self.state_file, "w") as f:
            json.dump(self.state, f, indent=4)
