from queue import SimpleQueue
from typing import Callable
from .entity import Entity

class BranchAndBound:
    """
    Обобщённый решатель методом ветвей и границ.
    """

    def __init__(self, initial: Entity | None, verbose = False):
        """
        Параметры
        ---------
        initial : Entity
            Начальный узел (корень дерева перебора).
        """
        if initial:
            self.initial = initial
        self.verbose = verbose
        self.entityHashes = set()

    def solve(self):
        queue = SimpleQueue[Entity]()
        queue.put(self.initial)
        i = 0
        deaph = 0
        added = 0
        corrected = 0
        while not queue.empty():
            entity = queue.get()
            if deaph != entity.deaph:
                print(f"Deaph {deaph}. Correct are {corrected} from {added}. It's {corrected / added * 100}%")
                deaph = entity.deaph
                added = 0
                corrected = 0

            if self.verbose and (i % 50 == 0):
                print(f"{i}. {entity}")
            i += 1

            if entity.isComplete():
                if entity.isSuitable():
                    h = entity.pack()
                    if h not in self.entityHashes:
                        self.entityHashes.add(h)
                continue

            for child in entity.branches():
                added += 1
                if child.isCorrect():
                    corrected += 1
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