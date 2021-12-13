import functools

from tri_declarative import shortcut


def superinvoking_shortcut(shortcut):
    @functools.wraps(shortcut)
    def wrapped(cls, **kwargs):
        def super_shortcut(**kwargs):
            parent_classmethod = vars(cls.__base__)[shortcut.__name__]
            undecorated_parent = parent_classmethod.__func__
            return undecorated_parent(cls, **kwargs)

        return shortcut(cls, super_shortcut=super_shortcut, **kwargs)

    return wrapped


def with_defaults(__target__=None, **decorator_kwargs):
    def decorator(__target__):
        @functools.wraps(__target__)
        @shortcut
        def wrapped_shortcut(*args, **kwargs):
            instance = __target__(*args, **kwargs)

            name = __target__.__name__
            if name == '__init__':
                args[0].refine_from_constructor(**decorator_kwargs)
            else:
                instance = instance.refine_from_shortcut(**decorator_kwargs)

                shortcut_stack = [name] + getattr(instance, '__tri_declarative_shortcut_stack', [])
                try:
                    instance.__tri_declarative_shortcut_stack = shortcut_stack
                except AttributeError:
                    pass

            return instance
        return wrapped_shortcut

    if __target__ is not None:
        return decorator(__target__)

    return decorator
