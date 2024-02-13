# UI imports
from PyQt6 import uic
from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import QApplication, QLineEdit
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

# backend imports
import sys
from functools import partial

from llm_backend import Interface


class CheckingTextBox:
    """ A text box that checks its text and changes colour based on correctness. """

    def __init__(self, line_edit, valid_words):
        """ Creates a text box with a visual input correctness indicator.
        :param line_edit:       textbox element
        :param valid_words:     list of valid words
        """

        self._line_edit = line_edit
        self._validation_rule = lambda text: text.lower() in valid_words

        # create stylesheets
        self._original_stylesheet = self._line_edit.styleSheet()
        self._incorrect_stylesheet = 'background-color: rgba(200, 0, 0, 0.2);'
        self._correct_stylesheet = 'background-color: rgba(0, 200, 0, 0.2);'

    def check_text(self):
        """ Checks if the current text is valid, changes styling to signal correct/incorrect input. """

        text = self._line_edit.text()

        # if the input is none, revert to default styling
        if text == '':
            self._line_edit.setStyleSheet(self._original_stylesheet)
            return

        # if the input is correct, set colour to green
        if self._validation_rule(text):
            self._line_edit.setStyleSheet(self._correct_stylesheet)
            return

        # set to incorrect stylesheet otherwise
        self._line_edit.setStyleSheet(self._incorrect_stylesheet)


def handle_input(input_field, chat_label, sound_button, sound_player, llm, context) -> None:
    """ Function for handling text input from the user.
    :param input_field:     text field from which input text is taken
    :param chat_label:      label where the chat history is set
    :param sound_button:    button that triggers sound to re-play
    :param sound_player:    sound player
    :param llm:             language model
    :param context:         context of the language model
    :param language:        second language of the language model
    """

    global history

    # get text and reset input field
    text = input_field.text()
    input_field.clear()

    # generate responses
    response_eng, response_lang = llm.get_response(context, text)

    # refresh the sound player source after new file has been generated
    sound_player.setSource(QUrl.fromLocalFile("temp.mp3"))
    sound_player.setSource(QUrl.fromLocalFile('voice.mp3'))
    sound_button.clicked.connect(sound_player.play)

    # update the text display with the new response added
    history += f"\nYou: {text}\n" + f"Baker: {response_lang}\n[{response_eng}]\n"
    chat_label.setText(history)

    # play the sound
    sound_player.play()


def main():
    """ Application runner. """

    # create the backend
    language = 'it'
    context = 'bakery.'
    llm = Interface(language)

    # load the UI
    app = QApplication(sys.argv)
    window = uic.loadUi('base.ui')
    window.background.setStyleSheet('background-image: url(background.png)')

    # hard-code the five example words
    word_list = ['pane', 'prezzo', 'fresco/fresca', 'dolce', 'farina']
    word_boxes = []

    # put the words into their respective text fields
    for num, words in zip(range(1, 6), word_list):

        # find the label element
        element = window.findChild(QLineEdit, f'word{num}textField')

        # create the textbox
        textbox = CheckingTextBox(element, words.split('/'))
        word_boxes.append(textbox)
        element.returnPressed.connect(textbox.check_text)

    # create the audio player
    sound_player = QMediaPlayer()
    audio_output = QAudioOutput()
    sound_player.setAudioOutput(audio_output)
    audio_output.setVolume(50)

    window.userInput.returnPressed.connect(partial(
        handle_input,window.userInput, window.outputText, window.playSound, sound_player,
        llm, context))
    window.show()

    sys.exit(app.exec())


# initialise chat history
global history
history = ''

if __name__ == '__main__':
    main()