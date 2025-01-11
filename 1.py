import sys
import boto3
import base64
import pygame
from PySide6.QtWidgets import (
    QApplication, QVBoxLayout, QWidget, QLabel, QLineEdit,
    QPushButton, QComboBox, QTextEdit, QMainWindow, QHBoxLayout
)

class TranslatorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Translator App")
        self.setGeometry(100, 100, 600, 400)

        # Initialize AWS Translate client with a specific region
        self.translate_client = boto3.client('translate', region_name='us-east-1')  # Replace with your preferred region
        self.polly_client = boto3.client('polly')

        # Setup UI elements and handlers here...
        self.init_ui()

    def init_ui(self):
        # Create central widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Create layout
        layout = QVBoxLayout(central_widget)

        # Input text
        self.input_label = QLabel("Enter text to translate:")
        self.input_text = QLineEdit()
        layout.addWidget(self.input_label)
        layout.addWidget(self.input_text)

        # Target language dropdown
        self.language_label = QLabel("Select target language:")
        self.language_dropdown = QComboBox()
        self.language_dropdown.addItems(["French", "German", "Spanish", "Chinese", "Tamil"])
        layout.addWidget(self.language_label)
        layout.addWidget(self.language_dropdown)

        # Translate button
        self.translate_button = QPushButton("Translate")
        self.translate_button.clicked.connect(self.translate_text)
        layout.addWidget(self.translate_button)

        # Translated text display
        self.translated_label = QLabel("Translation:")
        self.translated_text = QTextEdit()
        self.translated_text.setReadOnly(True)
        layout.addWidget(self.translated_label)
        layout.addWidget(self.translated_text)

        # Play audio button
        self.play_audio_button = QPushButton("Play Pronunciation")
        self.play_audio_button.clicked.connect(self.play_audio)
        self.play_audio_button.setEnabled(False)  # Initially disabled
        layout.addWidget(self.play_audio_button)

        self.audio_data = None  # Placeholder for audio data

    def translate_text(self):
        text = self.input_text.text()
        target_language = self.language_dropdown.currentText().lower()

        # Language mapping
        language_map = {
            "french": {"code": "fr", "voice": "Celine"},
            "german": {"code": "de", "voice": "Hans"},
            "spanish": {"code": "es", "voice": "Lucia"},
            "chinese": {"code": "zh", "voice": "Zhiyu"},
            "tamil": {"code": "ta", "voice": "Aditi"}  # Added Tamil
        }

        language_data = language_map.get(target_language)
        if not language_data:
            self.translated_text.setText("Unsupported language.")
            return

        try:
            # AWS Translate
            translate_response = self.translate_client.translate_text(
                Text=text,
                SourceLanguageCode="en",
                TargetLanguageCode=language_data["code"]
            )
            translated_text = translate_response['TranslatedText']
            self.translated_text.setText(translated_text)

            # AWS Polly
            polly_response = self.polly_client.synthesize_speech(
                Text=translated_text,
                OutputFormat="mp3",
                VoiceId=language_data["voice"]
            )
            self.audio_data = polly_response['AudioStream'].read()
            self.play_audio_button.setEnabled(True)  # Enable playback button

        except Exception as e:
            self.translated_text.setText(f"Error: {str(e)}")

    def play_audio(self):
        if not self.audio_data:
            print("No audio data available.")
            return

        # Write audio to temporary file
        audio_path = "temp_audio.mp3"
        with open(audio_path, "wb") as audio_file:
            audio_file.write(self.audio_data)

        # Check if the file exists
        import os
        if os.path.exists(audio_path):
            print(f"Audio file created: {audio_path}")
        else:
            print(f"Error: Audio file not created!")

        # Initialize pygame mixer
        pygame.mixer.init()

        # Load the audio file
        pygame.mixer.music.load(audio_path)

        # Play the audio
        pygame.mixer.music.play()

        print("Audio playback started.")

# Run the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TranslatorApp()
    window.show()
    sys.exit(app.exec())
