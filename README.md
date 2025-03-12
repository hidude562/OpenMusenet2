# Announcing... OpenMusenet3!
An expanded and enhanced version of OpenAI's MuseNet, with modern architecure and (suspected to be) larger. Compared to musenet, At least to me, it is noticably more coherent, and its signicantly more creative.

## Samples (Alla Turca)

https://github.com/user-attachments/assets/b57798f9-b89d-446f-a359-43ccd5989410

https://github.com/user-attachments/assets/47bff3d5-7b34-40a4-b141-8cedcb654072

3 Hours of music from scratch: https://www.youtube.com/watch?v=p6JX07dAwFw&t=6815s

# Interactive notebook:
https://colab.research.google.com/drive/1R3SpV9sajWafITdToC2NOzTw8tkZYWZl?usp=sharing

## Library (WIP)
In OpenMusenet3 folder, there is a work in progress library in the works. If you want to use it right now, download it and navigate to examples and you can run the scripts. A notebook will be released eventually

## Architecture
- Trained for 4096 context tokens (Model is able to support up to 32k)
- 12 instruments (Unlike Musenet, the instruments aren't categorized by section, its basically part numbers)
- 4 dynamics
- Qwen-2 model, but with GPT-2 tokenizer?? (Works weirdly well)

## TODO:
- Notebook for interference
- Library

# OpenMusenet2 (Legacy)
Open source WIP recreation of OpenAi's musenet. This supports many of the features of the original Musenet by OpenAI such as multiple track support (altough not guided to specific instrument), 4 levels of dynamics, as well as the note start, length, and note. You can find more info in the OpenMusenet2 folder
