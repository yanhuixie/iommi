from copy import copy
from typing import List, Tuple

from tri_declarative import (
    declarative,
    dispatch,
    flatten,
    getattr_path,
    Namespace,
    Refinable,
    refinable,
)

from iommi.base import items


def prefixes(path):
    parts = [p for p in path.split('__') if p]
    for i in range(len(parts)):
        yield '__'.join(parts[: i + 1])


priorities = [
    'refine defaults',
    'table defaults',
    'member defaults',
    'constructor',
    'shortcut',
    'style',
    'base',
    'member',
    'refine',
]


class RefinedNamespace(Namespace):
    __iommi_refined_stack: List[Tuple[int, Namespace, str]]

    def __init__(self, _description, _parent, _defaults=False, *args, **kwargs):
        params = Namespace(*args, **kwargs)

        if isinstance(_parent, RefinedNamespace):
            parent_stack = object.__getattribute__(_parent, '__iommi_refined_stack')
        else:
            parent_stack = [(priorities.index('base'), _parent, 'base')]

        if _description not in priorities:
            if _defaults:
                prio = -1
            else:
                prio = len(priorities)
        else:
            prio = priorities.index(_description)

        if _defaults:
            stack = [(prio, params, _description)] + parent_stack
        else:
            stack = parent_stack + [(prio, params, _description)]

        stack.sort(key=lambda x: x[0])

        object.__setattr__(self, '__iommi_refined_stack', stack)
        missing = object()

        super(RefinedNamespace, self).__init__()

        for _description, params, _ in stack:
            for path, value in items(flatten(params)):
                found = False
                for prefix in prefixes(path):
                    existing = getattr_path(self, prefix, missing)
                    if existing is missing:
                        break
                    new_updates = getattr_path(params, prefix)

                    if isinstance(existing, RefinableObject):
                        if isinstance(new_updates, dict):
                            existing = existing._refine(_description=_description, _defaults=False, **new_updates)
                        else:
                            existing = new_updates
                        self.setitem_path(prefix, existing)
                        found = True

                    if isinstance(new_updates, RefinableObject):
                        if isinstance(existing, dict):
                            new_updates = new_updates._refine(_description=_description, _defaults=True, **existing)
                        self.setitem_path(prefix, new_updates)
                        found = True

                if not found:
                    self.setitem_path(path, value)

    def as_stack(self):
        return [
            (description, flatten(params))
            for _, params, description in object.__getattribute__(self, '__iommi_refined_stack')
        ]


def is_refinable_function(attr):
    return getattr(attr, 'refinable', False)


class EvaluatedRefinable(Refinable):
    pass


def evaluated_refinable(f):
    f = refinable(f)
    f.__iommi__evaluated = True
    return f


class RefinableMembers(Refinable):
    pass


def is_evaluated_refinable(x):
    return isinstance(x, EvaluatedRefinable) or getattr(x, '__iommi__evaluated', False)


@declarative(
    member_class=Refinable,
    parameter='refinable',
    is_member=is_refinable_function,
    add_init_kwargs=False,
)
class RefinableObject:
    iommi_namespace: Namespace
    is_refine_done: bool

    @dispatch()
    def __init__(self, namespace=None, **kwargs):
        if namespace is None:
            namespace = Namespace()
        else:
            namespace = Namespace(namespace)

        declared_items = self.get_declared('refinable')
        for name in list(kwargs):
            prefix, _, _ = name.partition('__')
            if prefix in declared_items:
                namespace.setitem_path(name, kwargs.pop(name))

        if kwargs:
            available_keys = '\n    '.join(sorted(declared_items.keys()))
            raise TypeError(
                f"""\
{self.__class__.__name__} object has no refinable attribute(s): {', '.join(f'"{k}"' for k in sorted(kwargs.keys()))}.
Available attributes:
    {available_keys}
"""
            )

        self.iommi_namespace = namespace
        self.is_refine_done = False

    def refine_done(self, parent=None):
        result = copy(self)
        del self

        assert not result.is_refine_done, f"refine_done() already invoked on {result!r}"

        if hasattr(result, 'apply_styles'):
            is_root = parent is None
            if is_root:
                result._iommi_style_stack = []
            else:
                result._iommi_style_stack = list(parent._iommi_style_stack)
            iommi_style = result.iommi_namespace.get('iommi_style')

            from iommi.style import resolve_style
            iommi_style = resolve_style(result._iommi_style_stack, iommi_style)
            result._iommi_style_stack += [iommi_style]
            result = result.apply_styles(result._iommi_style_stack[-1], is_root=is_root)

        # Apply config from result.namespace to result
        declared_items = result.get_declared('refinable')
        remaining_namespace = Namespace(result.iommi_namespace)
        for k, v in items(declared_items):
            if k == 'iommi_style':
                remaining_namespace.pop(k, None)
                continue
            if isinstance(v, Refinable):
                setattr(result, k, remaining_namespace.pop(k, None))
            else:
                if k in remaining_namespace:
                    setattr(result, k, remaining_namespace.pop(k))

        if remaining_namespace:
            available_keys = '\n    '.join(sorted(declared_items.keys()))
            raise TypeError(
                f"""\
{result.__class__.__name__} object has no refinable attribute(s): {', '.join(f'"{k}"' for k in sorted(remaining_namespace.keys()))}.
Available attributes:
    {available_keys}
"""
            )
        result.is_refine_done = True

        result.on_refine_done()

        return result

    def on_refine_done(self):
        pass

    def refine(self, **args):
        return self._refine(_description='refine', _defaults=False, **args)

    def refine_defaults(self, **args):
        return self._refine(_description='refine defaults', _defaults=True, **args)

    def refine_from_constructor(self, **args):
        self._refine(_description='constructor', _defaults=False, _inplace=True, **args)

    def refine_from_member(self, **args):
        return self._refine(_description='member', _defaults=False, **args)

    def refine_from_member_defaults(self, **args):
        return self._refine(_description='member defaults', _defaults=True, **args)

    def refine_from_shortcut(self, **args):
        return self._refine(_description='shortcut', _defaults=True, **args)

    def refine_from_table_defaults(self, **args):
        return self._refine(_description='table defaults', _defaults=True, **args)

    def refine_from_style(self, **args):
        return self._refine(_description='style', _defaults=True, **args)

    def _refine(self, _description, _defaults, _inplace=False, **args):
        assert not self.is_refine_done, f"Already called refine_done on {self!r}"
        if _inplace:
            result = self
        else:
            result = copy(self)

        result.iommi_namespace = RefinedNamespace(_description, self.iommi_namespace, _defaults=_defaults, **args)
        return result

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.iommi_namespace}>"
