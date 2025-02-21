import os
import json
from datetime import datetime
from typing import List, Dict
import openai
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class ChatApp:
    def __init__(self):
        # Initialize OpenAI client
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in .env file")
            
        self.client = openai.OpenAI(
            api_key=api_key
        )
        
        # Initialize conversation history
        self.messages: List[Dict] = []
        self.history_file = Path('chat_history.json')
        
        # Load existing history if available
        self.load_history()

    def load_history(self) -> None:
        """Load chat history from file if it exists."""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    self.messages = json.load(f)
                print("Previous chat history loaded.")
            except json.JSONDecodeError:
                print("Error loading chat history. Starting fresh.")
                self.messages = []
        else:
            self.messages = []

    def save_history(self) -> None:
        """Save chat history to file."""
        with open(self.history_file, 'w') as f:
            json.dump(self.messages, f, indent=2)

    def get_ai_response(self, user_input: str) -> str:
        """Get response from OpenAI API."""
        # Add user message to history
        self.messages.append({"role": "user", "content": user_input})
        
        try:
            # Get response from OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=self.messages,
                temperature=0.7,
                max_tokens=150
            )
            
            # Extract and store AI response
            ai_response = response.choices[0].message.content
            self.messages.append({"role": "assistant", "content": ai_response})
            
            # Save updated history
            self.save_history()
            
            return ai_response
            
        except Exception as e:
            return f"Error: {str(e)}"

    def start_chat(self) -> None:
        """Start the chat interface."""
        print("\nWelcome to Terminal Chat!")
        print("Type 'quit' to exit, 'new' to start a new chat, or 'history' to view chat history.")
        
        while True:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() == 'quit':
                print("Goodbye!")
                break
                
            elif user_input.lower() == 'new':
                self.messages = []
                self.save_history()
                print("\nStarting new chat...")
                continue
                
            elif user_input.lower() == 'history':
                print("\nChat History:")
                for msg in self.messages:
                    role = "You" if msg["role"] == "user" else "AI"
                    print(f"\n{role}: {msg['content']}")
                continue
                
            elif not user_input:
                continue
                
            # Get and display AI response
            print("\nAI:", self.get_ai_response(user_input))

def main():
    try:
        # Start chat application
        chat_app = ChatApp()
        chat_app.start_chat()
    except ValueError as e:
        print(f"\nError: {e}")
        print("Please create a .env file with your OpenAI API key:")
        print("OPENAI_API_KEY=your-api-key-here")

if __name__ == "__main__":
    main()