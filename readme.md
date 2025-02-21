# Terminal AI Chat Application

A command-line chat application that allows you to interact with OpenAI's GPT models, including support for image analysis.

## Features

- Interactive terminal-based chat interface
- Support for both text and image inputs
- Conversation memory (saves chat history)
- Environment-based configuration
- Simple command system for managing chats

## Prerequisites

- Python 3.9 or higher
- OpenAI API key

## Installation

1. Clone the repository or download the source code.

2. Install the required packages:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root directory with your OpenAI API key:
```
OPENAI_API_KEY=your-api-key-here
```

## Usage

1. Start the application:
```bash
python chat_with_media.py
```

2. Available commands:
- `quit`: Exit the application
- `new`: Start a fresh chat
- `history`: View chat history

3. To include images in your prompts, enclose the image URL in double braces:
```
What's in this image? {{https://example.com/image.jpg}}
```

## Example Usage

```
Welcome to Terminal Chat!
Type 'quit' to exit, 'new' to start a new chat, or 'history' to view chat history.
To include images, enclose the image URL in double braces: {{image_url}}

You: Hello! How are you?
AI: Hello! I'm doing well, thank you for asking. How can I help you today?

You: What's in this image? {{https://example.com/image.jpg}}
AI: [AI will analyze and describe the image]

You: history
[Shows all previous messages in the current session]

You: new
Starting new chat...

You: quit
Goodbye!
```

## File Structure

```
.
├── chat_with_media.py  # Main application file
├── requirements.txt    # Python dependencies
├── .env                # Environment variables (create this)
└── chat_history.json   # Automatically created chat history file
```

## Technical Details

- Uses OpenAI's Python SDK for API interactions
- Automatically saves chat history to a JSON file
- Handles both text and image inputs
- Manages conversation context

## Error Handling

The application includes error handling for:
- Missing API keys
- Invalid image URLs
- API request failures
- Chat history file corruption

## Future Improvements

Potential enhancements could include:
- Local image file support
- Custom prompt templates
- Multiple conversation threads
- Chat export functionality
- Rate limiting handling
- Proxy support

## Contributing

Feel free to fork the repository and submit pull requests for any improvements.

## License

This project is open source and available under the MIT License.