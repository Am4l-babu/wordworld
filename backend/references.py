"""Typed, request-local discourse references; no cross-user/global scene state."""
from dataclasses import dataclass, replace


class UnresolvedReference(ValueError):
    pass


@dataclass
class Referent:
    type: str
    count: int
    action_index: int


class ReferenceContext:
    def __init__(self):
        self.groups: list[Referent] = []

    def introduce(self, kind, count, action_index, new_clause=False):
        if new_clause:
            self.groups = []
        self.groups.append(Referent(kind, count, action_index))

    def resolve(self, word):
        if not self.groups:
            raise UnresolvedReference(f"'{word}' has no object antecedent in this command.")
        if word.lower() == 'it':
            if self.groups[-1].count != 1:
                raise UnresolvedReference("'it' needs one unambiguous object, not a plural group.")
            return [replace(self.groups[-1])]
        if sum(group.count for group in self.groups) < 2:
            raise UnresolvedReference("'them' needs a plural antecedent in this command.")
        return [replace(group) for group in self.groups]

    def consume(self, kind, count):
        remaining = count
        for group in reversed(self.groups):
            if group.type == kind:
                removed = group.count if count == 'all' else min(group.count, remaining)
                group.count -= removed
                if count != 'all':
                    remaining -= removed
        self.groups = [group for group in self.groups if group.count]

    def removals(self, word, requested=None):
        groups = self.resolve(word)
        totals = {}
        for group in groups:
            totals[group.type] = totals.get(group.type, 0) + group.count
        available = sum(totals.values())
        notice = None
        if requested is not None and requested < available and len(totals) > 1:
            raise UnresolvedReference("A partial removal from a mixed collection needs an explicit object type.")
        if requested is not None and requested > available:
            notice = f"Reference contains only {available} objects; removal was limited to that collection."
        if requested is not None and len(totals) == 1:
            kind = next(iter(totals))
            totals[kind] = min(requested, available)
        return groups, [(kind, count) for kind, count in totals.items() if count], notice
