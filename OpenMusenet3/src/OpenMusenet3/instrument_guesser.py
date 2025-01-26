# TODO: The model labels the relative tracks and assigns them a guess of the instrument

from transformers import pipeline

class InstrumentGuesser:
    def __init__(self, model="hidude562/openmusenet-tracks-to-instruments"):
        self._model = pipeline(model=model, device="auto")
        
