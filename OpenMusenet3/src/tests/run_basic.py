from src.OpenMusenet3.ai import AI
from src.OpenMusenet3.ai import MIDI


ai = AI("kobimusic/esecutore-4-0619", device='cpu') # Change to 'cuda' if you have access to a gpu
mid = MIDI() # Pass in midi file, like "test2.mid"

# Default amount is 2000 new tokens
generations = ai.continueMusic("classical", mid, new_tokens=2000)
for i, generation in enumerate(generations):
    generation.save(f"AIPiece{i}.mid")