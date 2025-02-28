import os
import json
import re
import base64
import asyncio
import threading
import time
from datetime import datetime
from typing import List, Dict, Union, Tuple
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
        
        # Flag to track if response is being generated
        self.is_generating = False
        
        # Store the last response
        self.last_response = None

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

    def extract_image_references(self, text: str) -> Tuple[List[str], List[str]]:
        """
        Extract image URLs and file paths enclosed in double braces from text.
        Returns tuple of (urls, file_paths)
        """
        pattern = r'\{\{(.*?)\}\}'
        references = re.findall(pattern, text)
        
        urls = []
        file_paths = []
        
        for ref in references:
            ref = ref.strip()
            # Determine if it's a URL or file path
            if ref.startswith(('http://', 'https://')):
                urls.append(ref)
            else:
                # Treat as file path
                file_paths.append(ref)
                
        return urls, file_paths
    
    def encode_image_to_base64(self, image_path: str) -> str:
        """Encode an image file to base64."""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"Error encoding image {image_path}: {str(e)}")
            return None

    def create_message_content(self, text: str, image_urls: List[str], image_paths: List[str]) -> Union[str, List[Dict]]:
        """Create message content with text, image URLs, and local image files."""
        if not image_urls and not image_paths:
            return text

        # Remove the image placeholders from the text
        clean_text = re.sub(r'\{\{.*?\}\}', '', text).strip()
        
        # Create content list with text and images
        content = []
        
        # Add text if present
        if clean_text:
            content.append({
                "type": "text",
                "text": clean_text
            })
        
        # Add remote images (URLs)
        for url in image_urls:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": url
                }
            })
            
        # Add local images (file paths)
        for path in image_paths:
            # Skip if path doesn't exist
            if not os.path.exists(path):
                print(f"Warning: Image file not found: {path}")
                continue
                
            # Encode image to base64
            base64_image = self.encode_image_to_base64(path)
            if base64_image:
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                })
            
        return content

    def get_ai_response(self, user_input: str) -> None:
        """Get response from OpenAI API."""
        # Extract image references from input
        image_urls, image_paths = self.extract_image_references(user_input)
        
        # Create message content
        content = self.create_message_content(user_input, image_urls, image_paths)
        
        # Add user message to history
        self.messages.append({
            "role": "user",
            "content": content
        })
        
        try:
            # Get response from OpenAI
            has_images = len(image_urls) > 0 or len(image_paths) > 0
            model = "gpt-4o-mini"
            max_tokens = 4096
            
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
            
            # Store the response
            self.last_response = ai_response
            
        except Exception as e:
            self.last_response = f"Error: {str(e)}"
        
        # Mark response generation as complete
        self.is_generating = False

    def format_history_content(self, content) -> str:
        """Format message content for display in history."""
        if isinstance(content, str):
            return content
            
        if isinstance(content, list):
            parts = []
            for item in content:
                if item["type"] == "text":
                    parts.append(item["text"])
                elif item["type"] == "image_url":
                    url = item["image_url"].get("url", "")
                    # For local images (base64), show a placeholder instead of the entire string
                    if url.startswith("data:image"):
                        parts.append("[Local image]")
                    else:
                        parts.append(f"[Image: {url}]")
            return " ".join(parts)
        
        return str(content)

    def show_thinking_animation(self):
        """Display a thinking animation while waiting for AI response."""
        animation = "|/-\\"
        idx = 0
        start_time = time.time()
        
        # Continue until response is ready or timeout (60 seconds)
        while self.is_generating and time.time() - start_time < 60:
            print(f"\rAI thinking {animation[idx % len(animation)]}", end="")
            idx += 1
            time.sleep(0.1)
        
        # Clear the animation line
        print("\r" + " " * 20 + "\r", end="")

    def request_async_response(self, user_input: str):
        """Start an asynchronous request for AI response."""
        self.is_generating = True
        
        # Start the AI response in a separate thread
        thread = threading.Thread(target=self.get_ai_response, args=(user_input,))
        thread.daemon = True
        thread.start()
        
        # Show thinking animation while waiting
        self.show_thinking_animation()
        
        # Display the response once it's ready
        if self.last_response:
            print(f"AI: {self.last_response}")
        else:
            print("AI: Sorry, I couldn't generate a response.")

    def start_chat(self) -> None:
        """Start the chat interface."""
        print("\nWelcome to Terminal Chat!")
        print("Type 'quit' to exit, 'new' to start a new chat, or 'history' to view chat history.")
        print("To include images:")
        print("  - Remote images: {{https://example.com/image.jpg}}")
        print("  - Local images: {{/path/to/image.jpg}}")
        
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
                    formatted_content = self.format_history_content(msg["content"])
                    print(f"\n{role}: {formatted_content}")
                continue
                
            elif not user_input:
                continue
                
            # Get and display AI response asynchronously
            self.request_async_response(user_input)

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