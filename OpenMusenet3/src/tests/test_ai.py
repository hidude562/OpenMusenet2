import sys
import unittest
from unittest.mock import patch, MagicMock

# Mock heavy dependencies not needed for OpenRouter testing
# This needs to be done BEFORE the modules that import them are loaded.
sys.modules['torch'] = MagicMock()
mock_transformers = MagicMock()
mock_transformers.Qwen2ForCausalLM = MagicMock()
mock_transformers.GPT2TokenizerFast = MagicMock()
sys.modules['transformers'] = mock_transformers

import requests # Required for requests.exceptions.HTTPError

# Now import the modules under test
from OpenMusenet3.ai import AI
from OpenMusenet3.midi import MIDI

class TestOpenRouterAI(unittest.TestCase):
    def setUp(self):
        self.dummy_api_key = "dummy_key"
        self.openrouter_model_name = "openrouter/auto"
        # Create a MIDI object that can be used across tests
        # It's empty by default, which is fine for these tests
        self.midi_obj = MIDI()

    @patch('OpenMusenet3.ai.requests.post')
    def test_openrouter_generation_success(self, mock_post):
        # Configure the mock response for successful generation
        mock_response = MagicMock()
        mock_response.status_code = 200
        # Corrected AI format: start_time_delta<velocity_char>length<channel_char>note_number
        # Example: Note 1: Start 0, Vel '@'(60), Len 480, Chan '('(14), Note 72 (C5)
        #          Note 2: Start 240 (relative), Vel '@'(60), Len 240, Chan ')'(9), Note 60 (C4)
        # Note: The actual parsing logic in utils.parseNote seems to split numbers and non-numbers.
        # "0@480(72" -> parts: ["0", "@", "480", "(", "72"]
        # "240@240)60" -> parts: ["240", "@", "240", ")", "60"]
        # Add a trailing pipe to work with the current slicing logic in AI.continueMusic
        # generation = generation[:generation.rfind("|")]
        ai_content = "0@480(72|240@240)60|"
        mock_response.json.return_value = {
            "choices": [{"message": {"content": ai_content}}]
        }
        mock_post.return_value = mock_response

        # Instantiate AI for OpenRouter
        ai = AI(modelName=None, api_key=self.dummy_api_key, openrouter_model_name=self.openrouter_model_name)

        # Call continueMusic
        prompt = "test prompt"
        generated_midis = ai.continueMusic(prompt, self.midi_obj)

        # Assertions
        mock_post.assert_called_once()

        # Check the payload of the actual call (optional, but good for detailed testing)
        actual_call_args = mock_post.call_args
        payload = actual_call_args.kwargs['json']
        self.assertEqual(payload['model'], self.openrouter_model_name)
        self.assertEqual(payload['prompt'], f". {prompt} |{self.midi_obj._getAIFormat()}") # Assuming _formatMidiAndPrompt and _abridgeInputs are called

        self.assertEqual(len(generated_midis), 1)
        returned_midi = generated_midis[0]

        # The AI format "C5|1.0|0.5 G5|1.0|0.5" should be appended.
        # Depending on MIDI class implementation, check its internal state.
        # For this example, let's assume _getAIFormat reflects the notes added.
        # This assertion is highly dependent on the MIDI class's implementation.
        # If the initial midi_obj is empty, its AI format would be empty or minimal.
        # After appending, it should contain the new notes.
        # We need to know how _appendAIToSelf and _getAIFormat work.
        # For now, let's assume the final AI format string contains the generated part.
        # This part of the assertion might need refinement based on actual MIDI class behavior.
        # The _getAIFormat() will re-encode the notes. We expect the notes to be added.
        # A simple check is to see if the number of notes in the midi object has increased as expected.
        # Or, more robustly, check if _getAIFormat() output after generation contains representations
        # of the notes we "generated".
        # For now, let's check if the specific notes were added by looking at the AI format again.
        # This is a bit circular but confirms the data went through the process.
        # The exact string might differ due to timing adjustments or sorting.
        notes_found = []
        for track_idx, track in enumerate(returned_midi.tracks):
            for msg_idx, msg in enumerate(track):
                if hasattr(msg, 'note'):
                    notes_found.append(msg.note)

        self.assertIn(72, notes_found, f"Note 72 not found. Notes present: {notes_found}")
        self.assertIn(60, notes_found, f"Note 60 not found. Notes present: {notes_found}")


    @patch('OpenMusenet3.ai.requests.post')
    def test_openrouter_api_error(self, mock_post):
        # Configure the mock response for an API error
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("API Error")
        mock_post.return_value = mock_response

        # Instantiate AI for OpenRouter
        ai = AI(modelName=None, api_key=self.dummy_api_key, openrouter_model_name=self.openrouter_model_name)

        # Call continueMusic and assert that it raises an HTTPError
        prompt = "test prompt"
        with self.assertRaises(requests.exceptions.HTTPError):
            ai.continueMusic(prompt, self.midi_obj)

        # Assert that requests.post was called
        mock_post.assert_called_once()

if __name__ == '__main__':
    unittest.main()
