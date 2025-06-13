from src.OpenMusenet3.ai import AI
from src.OpenMusenet3.ai import MIDI


# Replace "YOUR_OPENROUTER_API_KEY" with your actual OpenRouter API key.
# You may also want to change the openrouter_model_name to a specific model.
# Set modelName to None as it's not used for OpenRouter.
ai = AI(modelName=None, device='cpu', openrouter_model_name="openrouter/auto", api_key="YOUR_OPENROUTER_API_KEY") # Change to 'cuda' if you have access to a gpu
mid = MIDI() # Pass in midi file, like "test2.mid"

# Default amount is 2000 new tokens
generations = ai.continueMusic("classical", mid, new_tokens=2000)
for i, generation in enumerate(generations):
    generation.save(f"AIPiece{i}.mid")