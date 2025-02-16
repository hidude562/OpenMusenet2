from OpenMusenet3.ai import AI
from OpenMusenet3.midi import MIDI

ai = AI("kobimusic/esecutore-4-0619")
mid = MIDI() # Pass in midi file, like "test2.mid"

# Default amount is 2000 new tokens
generations = ai.continueMusic("classical", mid, new_tokens=100)
for i, generation in enumerate(generations):
    generation.save(f"AIPiece{i}.mid")