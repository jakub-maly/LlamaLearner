# UI imports
from PyQt6 import uic
from PyQt6.QtCore import QTimer, QUrl
from PyQt6.QtWidgets import QApplication, QLineEdit
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

# backend imports
import sys
from functools import partial

from llm_backend import Interface


class FlashingTextBox:
    """ A text box that flashes green for correct input and red otherwise. """

    def __init__(self, line_edit, validation_rule):
        """ Creates a text box with a visual input correctness indicator.
        :param line_edit:       textbox element
        :param validation_rule: boolean function used for validating text input
        """

        self.line_edit = line_edit
        self.validation_rule = validation_rule

        # create stylesheets
        self.original_stylesheet = self.line_edit.styleSheet()
        # incorrect (red)
        self.flashing_stylesheet = "background-color: rgba(255, 0, 0, 0.2);"
        # correct (green)
        self.correct_stylesheet = "background-color: rgba(0, 255, 0, 0.2;"

        # bind flashing to a timer
        self.timer = QTimer()
        self.timer.timeout.connect(self._toggle_flash)

    def _toggle_flash(self):
        self.line_edit.setStyleSheet(
            self.flashing_stylesheet
            if self.line_edit.styleSheet() != self.flashing_stylesheet
            else self.original_stylesheet)

    def validate_and_flash(self):
        """ Checks if the current text is valid, changes styling to signal correct/incorrect input. """

        # if the input is correct
        if self.validation_rule(self.line_edit.text()):
            if self.timer.isActive():
                self.timer.stop()
            # Apply the correct stylesheet instead of resetting to the original
            self.line_edit.setStyleSheet(self.correct_stylesheet)
            return

        # otherwise start the timer to flash in 500ms intervals
        self.timer.start(500)


def handle_input(input_field, chat_label, sound_button, sound_player, llm, context, language) -> None:
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
    response_eng, response_lang = llm.get_response(context, text, language)

    # refresh the sound player source after new file has been generated
    sound_player.setSource(QUrl.fromLocalFile("temp.mp3"))
    sound_player.setSource(QUrl.fromLocalFile('voice.mp3'))
    sound_button.clicked.connect(sound_player.play)

    # update the text display with the new response added
    history += f"\nYou: {text}\n" + f"Baker: {response_lang}\n{response_eng}\n"
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

    # put the words into their respective text fields
    for num, words in zip(range(1, 6), word_list):

        # find the label element
        element = window.findChild(QLineEdit, f'word{num}textField')

        # create a function that checks if the correct word was input into a text field
        validation_rule = lambda text: text.lower() in words.split('/')

        # create the textbox
        textbox = FlashingTextBox(element, validation_rule)
        element.returnPressed.connect(textbox.validate_and_flash)

    # create the audio player
    sound_player = QMediaPlayer()
    audio_output = QAudioOutput()
    sound_player.setAudioOutput(audio_output)
    audio_output.setVolume(50)

    window.userInput.returnPressed.connect(
        partial(handle_input,
                window.userInput, window.outputText, window.playSound, sound_player,
                llm, context, language))
    window.show()

    sys.exit(app.exec())


# initialise chat history
global history
history = ''

if __name__ == '__main__':
    main()