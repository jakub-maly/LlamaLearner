## LLAMA learner (dem
*An interactive language learner app.*

Developed during AdaHack 23 to the following challenge: Design a mini-game that uses an open AI chatbot to teach players basic phrases or vocabulary through interactive dialogue.

### Functionality
The app allows you to have a bilingual conversation in a setting of your choice. The goal: ask the right questions to identify five basic vocabulary words.

Input is supported in both English and the second language of choice, and the app can even handle language mixing within a sentence! A locally installed `LLAMA2` LLM generates replies. All replies are printed in both languages, as well as played out loud using Google's text-to-speech models. The last reply can also be replayed by pressing the speaker button.

### Demo
The demo sets the second language to Italian and the setting to a bakery. Five simple words were generated using the LLM beforehand.
![image](https://github.com/jakub-maly/LlamaLearner/assets/50239149/df656473-cfca-4c38-a098-fee9a266feaf)

### Requirements
To run the program, Ollama's `LLAMA2` model needs to be installed locally, as well as the Python libraries `PyQt6`, `langchain`, `translate`, and `gtts`).
