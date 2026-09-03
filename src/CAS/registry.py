class Registry(dict):
    def register(self, name):
        def decorator(obj):
            if name in self:
                raise ValueError(f"'{name}' is already registered")
            self[name] = obj
        return decorator