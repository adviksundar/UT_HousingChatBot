# UT_HousingChatBot 🏠💬

A natural language chatbot that helps UT Austin students explore housing options in West Campus. It processes conversational queries and returns relevant listings using scraped Zillow data and a locally run LLaMA-2 model, presented through an interactive Gradio interface.

Originally developed as a group project for the Data Science Lab course at UT Austin, this version reflects additional work exploring LLM integration, prompt engineering, interface design, and local deployment.

---

## ✨ Project Overview

The chatbot combines geoscraped real estate data with a local language model to answer open-ended queries about rental preferences. Instead of relying on hardcoded filters, it uses LLaMA-2 to understand natural language and extract parameters like price range, bedrooms, or proximity to specific landmarks.

This version integrates:
- 💬 **LLaMA-2** for local query interpretation
- 🗺️ **Geoscraping** from Zillow for West Campus listings
- 🧠 Custom **prompt engineering** logic
- 🖥️ **Gradio interface** for clean user interaction
- ⚙️ **RTX 3050 local deployment** with CUDA acceleration

---

## 🧠 Key Areas of Work

### 🧩 LLM Integration
- Integrated **LLaMA-2 (7B chat)** via `llama-cpp-python` for on-device inference
- Developed the logic for passing structured prompts and interpreting outputs
- Handled constraints like filtering price, location, and room count from LLM responses

### ✍️ Prompt Engineering
- Designed prompt templates to yield structured, parsable responses
- Handled vague queries using fallback prompts and postprocessing
- Tuned format consistency for housing-specific language

### 🌍 Zillow Geoscraping
- Built and maintained a scraper to pull housing data from Zillow
- Captured metadata including price, location, amenities, and coordinates
- Enabled fuzzy location matching using UT landmarks

### 🖥️ Gradio Frontend
- Developed the chatbot UI using **Gradio**
- Integrated dynamic responses with listing previews
- Ensured smooth user interaction through real-time feedback and updates

### ⚙️ Deployment & Testing
- Ran and validated the system locally using an **RTX 3050 GPU**
- Used `llama-cpp-python[cuda]` for CUDA-accelerated inference
- Modularized code for scraping, querying, and interface logic

---

## HOW TO RUN THE CODE

### Download the LLaMA Model File (.gguf)

Same as before — manually download from:  
**TheBloke/Llama-2-7B-Chat-GGUF** on Hugging Face

> Model to download:  
`llama-2-7b-chat.Q4_K_M.gguf`

> Save into:  
`models/llama-2-7b-chat.Q4_K_M.gguf`

---

### Fork the Repository

Fork this repository into your GitHub account and clone it locally.

---

### Cd into re_chatbot

```bash
cd re_chatbot
```

---

### Run the following commands

```bash
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.venv\Scripts\Activate.ps1
```

If you’re using **VS Code**:  
Press `Ctrl + Shift + P` → **Python: Select Interpreter**  
Pick the one whose path ends in `.venv\Scripts\python.exe`.

---

### Upgrade pip

```bash
python -m pip install --upgrade pip
```

---

### Install dependencies

#### CPU build:
```bash
pip install pandas gradio llama-cpp-python
```

#### GPU build (works with your **RTX 3050**, needs CUDA 12+ runtime):
```bash
pip install pandas gradio "llama-cpp-python[cuda]"
```

---

### Run the program

```bash
python app\gradio_ui.py
```

---

## 📎 Original Project

This repo is based on a group project created for the Data Science Lab at UT Austin.  
Original team version: [abhidevireddy/UT_HousingChatBot](https://github.com/abhidevireddy/UT_HousingChatBot)

---

## 📝 Notes

This project offered hands-on experience in building a language model–driven system from end to end — combining web scraping, local model serving, structured prompting, UI development, and GPU deployment. The goal was to create a useful, accessible tool for students while exploring the integration of natural language interfaces with real-world data.
