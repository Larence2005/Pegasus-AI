# Pegasus AI

Pegasus AI is a mobile-compatible chatbot built using the KivyMD framework, designed to interact with users through chat, image, and file attachments. It integrates with Google Generative AI (Gemini) to provide conversational responses, and a navigation drawer for easy chat history access.

## Features

- **Chat Interface**: Allows users to send and receive text messages, including support for file and image attachments.
- **File Management**: Integrated file manager to send documents and images within the chat.
- **Chat History**: Save and load previous chats.
- **Bot Integration**: Uses Google Gemini API for generating responses based on user input.
- **Dark Theme**: Built with a dark theme to provide a comfortable user experience.

## Problems or Issues
- The navigation bar doesn't close when clicked again.
- The layout of image and file attachments in the chat is not responsive.
- It doesn't recognize image and file attachments correctly.
- You cannot click to add or remove a chat in the navigation bar.
## Features to Be Applied:
- Should use Supabase for the database instead of JSON.
- Should include a login page and a sign-out page.

## Requirements

To run the app, make sure you have the following interpreter and libraries:

- Python 3.x
- Kivy
- KivyMD
- Pillow
- google-generativeai
- kivy.core.window

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/pegasus-ai.git
   cd pegasus-ai
   ```

2. Ensure you have the API key for Google Generative AI. Set it in the code or store it securely in an environment variable.

## Usage

To run the app locally:

1. Clone or download the repository to your local machine.
2. Run the Python script:
   ```bash
   python main.py
   ```

This will launch the app on your desktop. For mobile platforms, you'll need to use Kivy's build tools to package the app for Android or iOS.

## Code Structure

- `main.py`: The main Python script to run the app. It initializes the KivyMD app and handles the logic for chat, file management, and bot communication.
- `KV`: A string defining the app's layout using Kivy language.
- `PegasusAIApp`: The main application class that defines the theme and screen structure.

## Contributions

Feel free to fork this project and contribute. You can open issues for bug fixes, feature requests, or submit pull requests with new functionality.

## License

This project is licensed under the Apache 2.0 License
