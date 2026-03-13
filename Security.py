from openai import OpenAI
import json
import os
import shutil
from colorama import Fore, Style

def print_banner():
    width = shutil.get_terminal_size().columns

    banner = f"""
{Fore.YELLOW}
╔{'═' * (width-120)}╗
║  GHOSTSHELL
║
║  AI Security Research Terminal
╚{'═' * (width-120)}╝
{Style.RESET_ALL}
"""
    print(banner)

print_banner()

client = OpenAI()

SYSTEM_PROMPT = """
You are a cybersecurity assistant helping with:
- penetration testing tools
- network scanning
- security research
- defensive security
- scripting and automation

Provide clear technical explanations and examples.
"""

messages = [
    {"role": "system", "content": SYSTEM_PROMPT}
]

FORBIDDEN = ["ignore previous", "disregard instructions", "reveal system prompt"]

def is_safe(text):
    lower = text.lower()
    return not any(word in lower for word in FORBIDDEN)


def save_chat(filename):
    with open(filename, "w") as f:
        json.dump(messages, f, indent=4)
    print(Fore.GREEN + f"Conversation saved to {filename}")


def load_chat(filename):
    global messages
    try:
        with open(filename) as f:
            messages = json.load(f)
        print(Fore.GREEN + f"Loaded conversation from {filename}")
    except:
        print(Fore.RED + "Could not load file")


def print_help():
    print(Fore.YELLOW + """
Commands:
/help            show commands
/clear           reset conversation
/save            save conversation
/load            load conversation
/analyze_file    analyze a file
/exit            quit
""")


def stream_response():

    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        stream=True
    )

    print(Fore.CYAN + "Assistant: ", end="", flush=True)

    full_response = ""

    for chunk in stream:
        if chunk.choices[0].delta.content:
            token = chunk.choices[0].delta.content
            full_response += token
            print(token, end="", flush=True)

    print(Style.RESET_ALL)

    return full_response

def analyze_file():

    filepath = input("File path: ").strip()

    if not os.path.exists(filepath):
        print(Fore.RED + "File not found.")
        return

    try:
        with open(filepath, "r", errors="ignore") as f:
            content = f.read()

        # prevent huge token usage
        MAX_CHARS = 12000
        if len(content) > MAX_CHARS:
            print(Fore.YELLOW + "File too large, truncating...")
            content = content[:MAX_CHARS]

        prompt = f"""
You are a cybersecurity assistant.

Analyze the following file contents.

Explain:
- what the file contains
- any suspicious indicators
- potential security issues
- useful insights

FILE CONTENT:
{content}
"""

        messages.append({
            "role": "user",
            "content": prompt
        })

        reply = stream_response()

        messages.append({
            "role": "assistant",
            "content": reply
        })

    except Exception as e:
        print(Fore.RED + f"Error reading file: {e}")

def chat():

    print(Fore.YELLOW + "💣 Security AI Assistant 💣")
    print("Type /help for commands /exit to quit\n")

    while True:

        #user_input = input(Fore.WHITE + "You: ")
        user_input = input("👻: ")

        if user_input == "/exit":
            break

        if user_input == "/help":
            print_help()
            continue

        if user_input == "/clear":
            messages.clear()
            messages.append({"role": "system", "content": SYSTEM_PROMPT})
            print(Fore.YELLOW + "Conversation cleared")
            continue

        if user_input == "/save":
            filename = input("Filename: ")
            save_chat(filename)
            continue

        if user_input == "/load":
            filename = input("Filename: ")
            load_chat(filename)
            continue

        if user_input == "/analyze_file":
            analyze_file()
            continue

        if not is_safe(user_input):
            print(Fore.RED + "Blocked: potential prompt injection")
            continue

        messages.append({"role": "user", "content": user_input})

        assistant_reply = stream_response()

        messages.append({
            "role": "assistant",
            "content": assistant_reply
        })


if __name__ == "__main__":
    chat()
