def builder(cls):
    class Builder:
        def __init__(self):
            self._kwargs = {}
            self._method_calls = []

        def __getattr__(self, name):
            if name.startswith("set_"):
                attr_name = name[4:]

                def setter(value):
                    self._kwargs[attr_name] = value
                    return self
                return setter

            elif hasattr(cls, name) and callable(getattr(cls, name)):
                def method_proxy(*args, **kwargs):
                    self._method_calls.append((name, args, kwargs))
                    return self
                return method_proxy

            raise AttributeError(f"'Builder' object has no attribute '{name}'")

        def build(self):
            obj = cls(**self._kwargs)
            for method_name, args, kwargs in self._method_calls:
                getattr(obj, method_name)(*args, **kwargs)
            return obj

    @classmethod
    def builder_classmethod(cls_):
        return Builder()

    setattr(cls, "builder", builder_classmethod)
    return cls
