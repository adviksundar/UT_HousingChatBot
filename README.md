# UT_HousingChatBot

HOW TO RUN THE CODE

Download the LLaMA Model File (.gguf)
Same as before — manually download:
    TheBloke/Llama-2-7B-Chat-GGUF on HuggingFace 
Model to download:
    llama-2-7b-chat.Q4_K_M.gguf
Save into:
    models/llama-2-7b-chat.Q4_K_M.gguf

Fork the repository
Cd into re_chatbot
Run the following commands
    python -m venv .venv
    Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
    .\.venv\Scripts\Activate.ps1
If you’re using VS code: 
    Press Ctrl Shift P → Python: Select Interpreter.
    Pick the one whose path ends in .venv\Scripts\python.exe.

Run this → python -m pip install --upgrade pip
Then run either of the following based on if you have gpu or cpu:
# CPU build
    pip install pandas gradio llama-cpp-python
# OR: GPU build (works with your RTX 4060, needs CUDA 12+ runtime)
    pip install pandas gradio "llama-cpp-python[cuda]"

Then run the program: python app\gradio_ui.py