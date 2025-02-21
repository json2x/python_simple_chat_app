import os
import json
import re
from datetime import datetime
from typing import List, Dict, Union
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

    def extract_image_urls(self, text: str) -> List[str]:
        """Extract image URLs enclosed in double braces from text."""
        pattern = r'\{\{(.*?)\}\}'
        return re.findall(pattern, text)

    def create_message_content(self, text: str, image_urls: List[str]) -> Union[str, List[Dict]]:
        """Create message content with text and images."""
        if not image_urls:
            return text

        # Remove the image URL placeholders from the text
        clean_text = re.sub(r'\{\{.*?\}\}', '', text).strip()
        
        # Create content list with text and images
        content = []
        
        # Add text if present
        if clean_text:
            content.append({
                "type": "text",
                "text": clean_text
            })
        
        # Add images with proper formatting
        for url in image_urls:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": url.strip()
                }
            })
            
        return content

    def get_ai_response(self, user_input: str) -> str:
        """Get response from OpenAI API."""
        # Extract image URLs from input
        image_urls = self.extract_image_urls(user_input)
        
        # Create message content
        content = self.create_message_content(user_input, image_urls)
        
        # Add user message to history
        self.messages.append({
            "role": "user",
            "content": content
        })
        
        try:
            # Get response from OpenAI
            model = "gpt-4o-mini"
            
            # Set max tokens based on model
            max_tokens = 4096 if image_urls else 512
            
            response = self.client.chat.completions.create(
                model=model,
                messages=self.messages,
                temperature=0.7,
                max_tokens=max_tokens
            )
            
            # Extract and store AI response
            ai_response = response.choices[0].message.content
            self.messages.append({
                "role": "assistant",
                "content": ai_response
            })
            
            # Save updated history
            self.save_history()
            
            return ai_response
            
        except Exception as e:
            return f"Error: {str(e)}"

    def start_chat(self) -> None:
        """Start the chat interface."""
        print("\nWelcome to Terminal Chat!")
        print("Type 'quit' to exit, 'new' to start a new chat, or 'history' to view chat history.")
        print("To include images, enclose the image URL in double braces: {{image_url}}")
        
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
                    content = msg["content"]
                    if isinstance(content, list):
                        # Handle messages with images
                        text_parts = [item["text"] for item in content if item["type"] == "text"]
                        image_parts = [f"[Image: {item['image_url']['url']}]" for item in content if item["type"] == "image_url"]
                        print(f"\n{role}: {''.join(text_parts)} {' '.join(image_parts)}")
                    else:
                        print(f"\n{role}: {content}")
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