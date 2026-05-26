from queue import SimpleQueue
from typing import Callable
from .entity import Entity

class BranchAndBound:
    """
    Обобщённый решатель методом ветвей и границ.
    """

    def __init__(self, initial: Entity, verbose = False):
        """
        Параметры
        ---------
        initial : Entity
            Начальный узел (корень дерева перебора).
        """
        self.initial = initial
        self.verbose = verbose
        self.entityHashes = set()

    def solve(self):
        queue = SimpleQueue[Entity]()
        queue.put(self.initial)
        i = 0
        while not queue.empty():
            entity = queue.get()
            if self.verbose:
                print(f"{i}. {entity}")
                i += 1

            if entity.isComplete():
                if entity.isSuitable():
                    h = entity.pack()
                    if h not in self.entityHashes:
                        self.entityHashes.add(h)
                continue

            for child in entity.branches():
                if child.isCorrect():
                    queue.put(child)
        return self.entityHashes

    def filterEntity(self, pred: Callable):
        self.entityHashes = {entity for entity in self.entityHashes if pred(entity)}

    def save_if(self, filename, pred, entities = None):
        if entities is None:
            entities = self.entityHashes
        with open(filename, "w") as f:
            f.writelines([f"{entity}\n" for entity in entities if pred(entity)])

    def save_transform(self, filename, frans, entities = None):
        if entities is None:
            entities = self.entityHashes
        with open(filename, "w") as f:
            f.writelines([f"{frans(entity)}\n" for entity in entities])

    def save(self, filename: str, entities = None):
        return self.save_if(filename, lambda x: True, entities=entities)

