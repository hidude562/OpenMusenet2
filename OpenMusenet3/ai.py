from transformers import AutoModelForCausalLM, AutoTokenizer
import copy
import huggingface_hub

from midi import MIDI

class AI:
    def __init__(self, modelName):
        self.modelName = modelName
        self.model = AutoModelForCausalLM.from_pretrained(modelName)
        self.tokenizer = AutoTokenizer.from_pretrained(self.modelName)

    """
    Returns the AI Format, (what is newly generated)
    """
    def _generateRawNoStream(self, txt: str, batch=4) -> str:
        inputs = self.tokenizer(txt, return_tensors="pt").input_ids
        output = self.model.generate(
            inputs,
            use_cache=False,
            max_new_tokens=2000,
            do_sample=True,
            temperature=0.89,
            top_p=1.0,
            num_return_sequences=batch,
        )
        decoded = self.tokenizer.batch_decode(output[:, inputs.shape[1]:])
        return decoded

    """
    Include only last 200 notes, which is 25% of input
    """
    def _abridgeInputs(self, inputStr):
        parts = inputStr.split('|')
        textBeforeFirstPipe= parts[0].lower() + "|"
        parts = parts[1:]
        textBeforeLastPipe = '|'.join(parts[-200:])

        return textBeforeFirstPipe + textBeforeLastPipe

    def _formatMidiAndPrompt(self, prompt: str, midi: MIDI) -> str:
        formatted = f". {prompt} |{midi._getAIFormat()}"
        return formatted

    """
    TODO: Stream outputs
    """
    def continueMusic(self, prompt: str, midi: MIDI) -> list[MIDI]:
        formatted = self._formatMidiAndPrompt(prompt, midi)
        formatted = self._abridgeInputs(formatted)
        generations = self._generateRawNoStream(formatted)
        midiConvertedGenerations = []
        for generation in generations:
            generation = generation[:generation.rfind("|")]
            print(generation)
            midiAddedGeneration = copy.deepcopy(midi)
            midiAddedGeneration._appendAIToSelf(generation)
            midiConvertedGenerations.append(midiAddedGeneration)
        return midiConvertedGenerations

ai = AI("kobimusic/esecutore-4-0619")
mid = MIDI("test2.mid")
generations = ai.continueMusic("classical", mid)
for i, generation in enumerate(generations):
    generation.save(f"AIPiece{i}.mid")