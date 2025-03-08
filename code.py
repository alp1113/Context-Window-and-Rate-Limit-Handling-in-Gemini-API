#!pip install google-generativeai Install command for the package

import google.generativeai as genai
import google.api_core.exceptions  # Import correct exception module
import time

from google.colab import userdata
key = userdata.get('GOOGLE_API_KEY')

# Configure the API key (Replace with your actual key)
genai.configure(api_key = key)

# Initialize Model and Constants
MODEL_NAME = genai.GenerativeModel("gemini-1.5-pro")


# Constants for context window tracking
MAX_TOKENS = 2048  # Adjust this based on Gemini's latest limits
WARNING_THRESHOLD = 0.8 * MAX_TOKENS  # Warn at 80% of max tokens

def count_tokens(text):
    return MODEL_NAME.count_tokğens(text).total_tokens  # Find number of tokens

#Text Generation

def generate_text(prompt, history=[]):
    request_size = count_tokens(prompt)  # Count tokens in the prompt

    # Generate response first
    response = retry_on_rate_limit(MODEL_NAME.generate_content, prompt)

    if response:
        response_size = count_tokens(response.text)  # Count response tokens
    else:
        return  # Handle failure case

    # Call check_context_window with history
    total_size = check_context_window(request_size, response_size, history)
    if total_size is False:
        return  # Stop execution if over limit

    print("\n💬 AI Response:\n", response.text)

    #Chat mode

    def chat_mode():
    chat = MODEL_NAME.start_chat()
    history = []  # Store conversation history

    # Initial prompt
    initial_prompt = "What is the capital of The Netherlands, and what are the overseas territories? Also, explain where the Kingdom of the Netherlands has constitutional and protectorational influence. Lastly, list all the provinces of the Netherlands (do mention overseas territories if there are any)."

    response = chat.send_message(initial_prompt)
    print(response.text)

    # Track context size
    request_size = count_tokens(initial_prompt)
    response_size = count_tokens(response.text)

    if check_context_window(request_size, response_size, history) is False:
        return  # Stop execution if over limit

    history.append(initial_prompt)
    history.append(response.text)

    # Additional test prompts
    test_prompts = [
        "How many provinces are there in the Netherlands?",
        "Tell me a long, detailed story about a cyberpunk world where AI controls everything, but a group of hackers plans to take it down.",
        "Write a 500-word essay on the history of the Roman Empire and its influence on modern governance.",
        "Explain quantum computing to a 5-year-old, then to a high school student, then to a PhD researcher, adjusting the complexity each time.",
        "Generate a detailed roadmap for learning artificial intelligence, from beginner to advanced level, with books, courses, and project ideas.",
        "Write an extensive comparison of Python and C++ for machine learning, covering syntax, performance, libraries, and real-world use cases.",
        "Describe a post-apocalyptic world where humanity survives underground, avoiding mutated creatures that roam the surface.",
        "Explain in-depth how neural networks function, including activation functions, backpropagation, and gradient descent.",
        "Write an advanced guide on reverse engineering software, including tools, techniques, and ethical considerations.",
        "Give me a step-by-step breakdown of how a large language model like Gemini is trained, including pretraining, fine-tuning, and inference.",
        "Write a dialogue between Nikola Tesla and Albert Einstein discussing modern artificial intelligence and its ethical implications."
    ]

    for idx, prompt in enumerate(test_prompts):
        print(f"\n Sending Prompt {idx+1}/{len(test_prompts)}: {prompt}")

        response = retry_on_rate_limit(chat.send_message, prompt)

        if response:
            print("\n✅ Response received successfully!")
            print(response.text)

            # Track context window
            request_size = len(prompt)
            response_size = len(response.text)

            if check_context_window(request_size, response_size, history) is False:
                return  # Stop execution if over limit

            history.append(prompt)
            history.append(response.text)

    return response

#Context Window Handling


def check_context_window(request_size, response_size, history=[]):
    # Compute previous conversation token count
    history_size = sum(count_tokens(msg) for msg in history)

    # Compute total token usage
    total_size = history_size + request_size + response_size
    #print(f"{'*' * 10} {total_size} {'*' * 10}")

    if total_size > WARNING_THRESHOLD and total_size < MAX_TOKENS:
        print(f"⚠️ Warning! Approaching context window limit ({total_size}/{MAX_TOKENS})")

    elif total_size > MAX_TOKENS:
        print(f"⚠️ Warning! Context window limit exceeded ({total_size}/{MAX_TOKENS})")

    return total_size  # Return total token usage

# Function to handle rate limits with retries
def retry_on_rate_limit(func, *args, retries=3, wait_time=2, **kwargs):
    for attempt in range(retries):
        try:
            return func(*args, **kwargs)  # Attempt API call
        except google.api_core.exceptions.TooManyRequests:  # Corrected exception
            print(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
            wait_time *= 2  # Exponential backoff
    raise Exception("Max retries reached. Program will stop.")  # Raise an exception to break the program
    return None

# Example Usage
if __name__ == "__main__":
    print("1.Text Generation Mode")
    print("2.Chat Mode")
    mode = input("Choose mode (1/2): ")

    if mode == "1":
        prompt = input("Enter your text prompt: ")
        generate_text(prompt)
    elif mode == "2":
        print("Enter 'exit' to quit chat mode.")
        chat_mode()
    else:
        print("Invalid option. Exiting.")