import torch
from transformers import Qwen2ForCausalLM, GPT2TokenizerFast
import copy

from midi import MIDI

class AI:
    def __init__(self, modelName, device='cuda'):
        self.modelName = modelName
        self.tokenizer = GPT2TokenizerFast.from_pretrained(self.modelName, padding_side='right')
        AutoModelForCausalLM.from_pretrained(model_name)

        self.device = device

        self.model.to(self.device)

    """
    Returns the AI Format, (what is newly generated)
    """
    def _generateRawNoStream(self, txt: str, batch_size=1, new_tokens=2000, temperature=0.86) -> str:
        inputs = torch.tensor(self.tokenizer.encode(txt)).unsqueeze(0)
        inputs = inputs.to(self.device)
        gen_length = len(inputs[0])

        print(txt)

        output = self.model.generate(
            inputs,
            max_length=gen_length + new_tokens,
            do_sample=True,
            temperature=temperature,
            top_p=1.0,
            repetition_penalty=1.0,
            top_k=20,
            num_return_sequences=batch_size,
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
    def continueMusic(self, prompt: str, midi: MIDI, batch_size=1, new_tokens=2000, temperature=0.86) -> list[MIDI]:
        formatted = self._formatMidiAndPrompt(prompt, midi)
        formatted = self._abridgeInputs(formatted)
        generations = self._generateRawNoStream(formatted, batch_size, new_tokens, temperature)
        midiConvertedGenerations = []
        for generation in generations:
            generation = generation[:generation.rfind("|")]
            midiAddedGeneration = copy.deepcopy(midi)
            midiAddedGeneration._appendAIToSelf(generation)
            midiConvertedGenerations.append(midiAddedGeneration)
        return midiConvertedGenerations
