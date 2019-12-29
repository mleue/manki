import click


class Deduplicator:
    def __init__(self, entity_type: str):
        self.entity_type = entity_type
        self.entities = {}

    def is_duplicate(self, entity, location: str):
        if entity in self.entities:
            self._log_duplicate(entity)
            return True
        else:
            self.entities[entity] = location
            return False

    def _log_duplicate(self, entity):
        initial_location = self.entities[entity]
        l1 = f"Duplicate {self.entity_type} encountered: '{str(entity)}'."
        l2 = f"First seen at '{initial_location}'."
        l3 = "Disregarding."
        click.echo(f"{l1}\n{l2}\n{l3}")
