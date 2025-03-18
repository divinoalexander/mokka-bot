import tkinter as tk
from tkinter import scrolledtext, font, ttk
from tkinter import messagebox
import json
from chat import get_response, load_chat_history
from PIL import Image, ImageTk  # For icons (install with `pip install pillow`)

# Modern color scheme
BG_COLOR = "#2E3440"  # Dark background
TEXT_COLOR = "#ECEFF4"  # Light text
USER_COLOR = "#88C0D0"  # Light blue for user messages
BOT_COLOR = "#A3BE8C"  # Light green for bot messages
ENTRY_COLOR = "#4C566A"  # Darker background for input field
BUTTON_COLOR = "#5E81AC"  # Blue for buttons
BUTTON_HOVER_COLOR = "#81A1C1"  # Lighter blue for button hover

# Load chat history
def load_existing_chat():
    try:
        chat_data = load_chat_history()
        for entry in chat_data.get("chat_history", []):
            chat_window.insert(tk.END, f"You: {entry['user']}\n", "user")
            chat_window.insert(tk.END, f"Bot: {entry['bot']}\n\n", "bot")
        chat_window.yview(tk.END)
    except Exception as e:
        print(f"Error loading chat history: {e}")
        chat_window.insert(tk.END, "Bot: Welcome to E-Commerce Product Chatbot! Ask me about any product.\n\n", "bot")

# Send message function
def send_message(event=None):
    user_input = entry.get()
    if user_input.strip():
        # Display user message
        chat_window.insert(tk.END, f"You: {user_input}\n", "user")
        chat_window.update_idletasks()

        # Disable input and send button while processing
        entry.config(state=tk.DISABLED)
        send_button.config(state=tk.DISABLED)

        # Display "Thinking..." message
        chat_window.insert(tk.END, "Bot: Thinking...\n\n", "bot")
        chat_window.yview(tk.END)

        # Get bot response
        response = get_response(user_input)

        # Remove "Thinking..." message and display bot response
        chat_window.delete("end-2l", "end-1c")  # Remove the last line
        chat_window.insert(tk.END, f"Bot: {response}\n\n", "bot")
        chat_window.yview(tk.END)

        # Re-enable input and send button
        entry.config(state=tk.NORMAL)
        send_button.config(state=tk.NORMAL)
        entry.delete(0, tk.END)

# Create main window
root = tk.Tk()
root.title("E-Commerce Product Chatbot")
root.geometry("700x800")
root.configure(bg=BG_COLOR)

# Custom font
custom_font = font.Font(family="Helvetica", size=12)

# Frame for the chat window
chat_frame = tk.Frame(root, bg=BG_COLOR)
chat_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

# Chat display area
chat_window = scrolledtext.ScrolledText(
    chat_frame,
    wrap=tk.WORD,
    width=70,
    height=25,
    font=custom_font,
    bg=BG_COLOR,
    fg=TEXT_COLOR,
    bd=0,
    relief=tk.FLAT,
    insertbackground=TEXT_COLOR,  # Cursor color
)
chat_window.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
chat_window.tag_config("user", foreground=USER_COLOR, font=custom_font)
chat_window.tag_config("bot", foreground=BOT_COLOR, font=custom_font)

# Frame for input area
input_frame = tk.Frame(root, bg=BG_COLOR)
input_frame.pack(fill=tk.X, padx=20, pady=10)

# User input field
entry = tk.Entry(
    input_frame,
    width=50,
    font=custom_font,
    bg=ENTRY_COLOR,
    fg=TEXT_COLOR,
    bd=0,
    relief=tk.FLAT,
    insertbackground=TEXT_COLOR,  # Cursor color
)
entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
entry.bind("<Return>", send_message)  # Bind Enter key to send message

# Send button with icon
send_icon = Image.open("send_icon.png")  # Replace with your icon path
send_icon = send_icon.resize((20, 20), Image.Resampling.LANCZOS)  # Updated resampling method
send_icon = ImageTk.PhotoImage(send_icon)

send_button = tk.Button(
    input_frame,
    image=send_icon,
    command=send_message,
    bg=BUTTON_COLOR,
    activebackground=BUTTON_HOVER_COLOR,
    bd=0,
    relief=tk.FLAT,
)
send_button.pack(side=tk.RIGHT, padx=5)

# Status message at the bottom
status_label = tk.Label(
    root,
    text="Connected to Amazon product database",
    font=("Helvetica", 10),
    fg=TEXT_COLOR,
    bg=BG_COLOR,
)
status_label.pack(pady=(0, 10))

# Load existing chat history
load_existing_chat()

# Run the application
root.mainloop()