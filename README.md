# OpenMusenet2
Open source WIP recreation of OpenAi's musenet. This supports many of the features of the original Musenet by OpenAI such as multiple track support (altough not guided to specific instrument), 4 levels of dynamics, as well as the note start, length, and note.

# Generating
Here is the <a href="https://colab.research.google.com/drive/1Rdu2R8vDt5PHUQKlP22AgWt7YfwBzahU?usp=sharing">Google Colab notebook</a> for generating.

# Samples

Fur Elise
https://github.com/hidude562/OpenMusenet2/assets/82677882/692dd270-8ffd-4967-9af7-d4aa612fbaf8


Allca turra
https://github.com/hidude562/OpenMusenet2/assets/82677882/6010b13e-1597-4604-8489-1156b0362cf6

# Technical things
The current model as of writing this is "OpenMusenet2.0", which is a finetuned version of gpt-2 medium on ~10,000 songs (Around 20kb per song). I don't remember where i got the dataset from (I had actually downloaded it the year prior), but it is ~169,000 midi files of types 0 and 1 with multiple tracks, tempo changes, etc.

# Training your own model/dataset
Go to "Notebooks" -> "Converters" -> "midiFormater.ipynb" and you can open that with Google Colab (or whatever notebook editor you use). The process from there should be relatively simple.

Once you've downloaded your data the process there will vary depending on what notebook you are using to train so i can't really ellaborate on that.

# Improvement ideas
<ul>
<li>Seperate drum track that is only for drums</li>
<li>Large version of model</li>
<li>Some midis are 10x the playback speed of what it should be (AI emulates this behavior)</li>
</ul>
