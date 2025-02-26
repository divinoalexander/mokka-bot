import tkinter as tk
from tkinter import scrolledtext
from chat import get_response

def send_message():
    user_input = entry.get()
    if user_input.strip():
        chat_window.insert(tk.END, "You: " + user_input + "\n", "user")
        response = get_response(user_input)
        chat_window.insert(tk.END, "Bot: " + response + "\n\n", "bot")
        entry.delete(0, tk.END)
        chat_window.yview(tk.END)

# Create main window
root = tk.Tk()
root.title("Chatbot with Web Scraping")
root.geometry("500x600")

# Chat display area
chat_window = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=60, height=20, font=("Arial", 12))
chat_window.pack(padx=10, pady=10)
chat_window.tag_config("user", foreground="blue")
chat_window.tag_config("bot", foreground="green")

# User input field
entry = tk.Entry(root, width=50, font=("Arial", 14))
entry.pack(padx=10, pady=5)
entry.bind("<Return>", lambda event: send_message())

# Send button
send_button = tk.Button(root, text="Send", command=send_message, font=("Arial", 12), bg="lightblue")
send_button.pack(pady=10)

# Run the application
root.mainloop()
