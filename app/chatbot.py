from llama_cpp import Llama

# Optimized model loading
llm = Llama(
    model_path= r"C:\Users\awert\RE_Chatbot\models\llama-2-7b-chat.Q4_K_M.gguf",
    n_ctx=2048,          # Context size (good default for chat)
    n_gpu_layers=35,     # Use GPU acceleration (RTX 3050: ~35 is safe)
    n_threads=8,         # Use 8 CPU threads to speed up CPU parts
    n_batch=256,         # Process 256 tokens per batch (faster, fits RTX 3050)
    use_mlock=True,      # Prevent model from being swapped to disk (faster, safer)
    use_mmap=True        # Faster memory loading
)

def chatbot_response(user_input):
    prompt = f"""You are a real estate assistant helping students at UT Austin.
    User: {user_input}
    Assistant:"""
    response = llm(
        prompt,
        max_tokens=512,
        stop=["User:", "Assistant:"],
        echo=False
    )
    return response["choices"][0]["text"].strip()
