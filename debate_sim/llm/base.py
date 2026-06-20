from abc import ABC
from abc import abstractmethod


class LLMProvider(ABC):

    @abstractmethod
    def generate(self, model, prompt):
        pass