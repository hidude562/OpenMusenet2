import torch
from transformers import Qwen2ForCausalLM, GPT2TokenizerFast
import copy
import requests # Added import

from .midi import MIDI # Changed to relative import

class AI:
    def __init__(self, modelName, device='cuda', api_key=None, openrouter_model_name=None): # Added parameters
        self.modelName = modelName
        self.device = device
        self.api_key = api_key # Added api_key
        self.openrouter_model_name = openrouter_model_name # Added openrouter_model_name
        self.use_openrouter = False # Added use_openrouter flag

        if self.openrouter_model_name:
            self.use_openrouter = True
            # Do not load Hugging Face tokenizer or model if openrouter_model_name is set
        else:
            self.tokenizer = GPT2TokenizerFast.from_pretrained(self.modelName, padding_side='right')
            self.model = Qwen2ForCausalLM.from_pretrained(self.modelName, load_in_16_bit=True)
            self.model.to(self.device)

    """
    Returns the AI Format, (what is newly generated)
    """
    def _generateRawNoStream(self, txt: str, batch_size=1, new_tokens=2000, temperature=0.86) -> str:
        if self.use_openrouter:
            payload = {
                "model": self.openrouter_model_name,
                "prompt": txt,
                "max_tokens": new_tokens,
                "temperature": temperature,
                # Add other relevant parameters like top_p, repetition_penalty, top_k if supported by OpenRouter
            }
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            response = requests.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)
            response.raise_for_status() # Raise an exception for bad status codes
            generated_text = response.json()['choices'][0]['message']['content']
            return [generated_text] # Return as a list containing one string
        else:
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
