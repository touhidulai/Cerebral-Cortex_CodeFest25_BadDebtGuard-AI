from huggingface_hub import InferenceClient
import sys
import io
import os
from extractor import extract_text  # import the universal extractor

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Replace with your HF token
HF_TOKEN = "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"

# Initialize HuggingFace client
client = InferenceClient(token=HF_TOKEN)

def chat(message, model="meta-llama/Llama-3.2-3B-Instruct"):
    """Send a message to the AI and get a response"""
    try:
        response = client.chat_completion(
            model=model,
            messages=[{"role": "user", "content": message}],
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"


print("Loan Risk Analyzer Ready! (Type 'quit' to exit)")
print("Use: parse <path-to-file> to analyze a loan essay.\n")


while True:
    user_input = input("You: ")

    # Exit command
    if user_input.lower() in ['quit', 'exit', 'bye']:
        print("Goodbye!")
        break

    # PARSE COMMAND
    if user_input.lower().startswith("parse "):
        # remove quotes and normalize path
        file_path = os.path.normpath(user_input[6:].strip().strip('"').strip("'"))
        print("\nExtracting text...\n")

        text = extract_text(file_path)

        if "Unsupported file type" in text or "Error" in text:
            print(f"\nAI: Extraction failed: {text}\n")
            continue

        # LLM prompt for risk classification
        prompt = f"""
You are an expert loan-risk assessment AI. 
The following text is a loan application essay.

Your tasks:
1. Classify the loan risk as one of: **High Risk**, **Medium Risk**, **Low Risk**.
2. Identify **only the 3 most important keywords or phrases** from the essay that justify this classification.
3. Provide a **concise explanation (1-3 sentences)** clearly linking the keywords to the risk level.
4. Do NOT include unnecessary text or unrelated details.
5. Output exactly in this format:

Risk Level: <High/Medium/Low>
Keywords Found: <keyword1, keyword2, keyword3>
Explanation: <1-3 sentences linking the keywords to the risk level>

Essay:
\"\"\"
{text}
\"\"\"
"""

        response = chat(prompt)
        print(f"\nAI: {response}\n")
        continue

    # NORMAL CHAT
    if user_input.strip():
        response = chat(user_input)
        print(f"\nAI: {response}\n")
