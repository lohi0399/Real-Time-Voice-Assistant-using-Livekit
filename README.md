# Hybrid Image Query Voice Assistant - Lohit Gandham

## Overview

This repository provides a solution to integrate a hybrid image processing system for **RoboLohit**, the real-time personalized assistant for the blind and visually impaired. The system dynamically switches between a proprietary model (e.g., GPT-4o) and an open-source model (**Groq LLaMA 3.2-11B Vision Preview**) based on the presence of a person in the image. The Groq model is used to describe images containing people, circumventing proprietary model guardrails, while maintaining high reliability and low latency.

---

## Features

- **Hybrid Model Handling**:
  - **Person Detected**: Uses the **Groq LLaMA 3.2-11B Vision Preview** model.
  - **No Person Detected**: Processes queries with GPT-4o.
- **Low Latency**: Achieves a time-to-first-token (TTFT) under 500ms for streamed responses.
- **Scalable Design**: Handles at least 10 image queries (split evenly between people-present and people-absent cases) in one API call without degradation in response times.
- **User-Friendly Deployment**: Minimal setup required for running the project.

---

## Prerequisites

1. **Python Environment**:
   - Python 3.8 or higher.
   - Required dependencies specified in `requirements.txt`.

2. **API Accounts**:
   - **Groq API**: Create a free account at [Groq Console](https://console.groq.com/login) and obtain your API key.
   - **LiveKit**: Create a free account at [LiveKit](https://livekit.io/) to get your LiveKit URL, API key, and secret.
   - **Other API Keys**: These include DeepGram, OpenAI, and Eleven Labs keys. Obtain these from the password-protected zip file provided via email (password also provided in the email).

3. **Hardware**:
   - Internet access for querying APIs.

---

## Setup

### Environment Setup

1. Create and activate a virtual environment:
   
   For Windows:
   
   ```bash
   python -m venv ally_env
   source .\ally_env\Scripts\activate.bat (run from the cmd)
   ```

   For Linux:

   ```bash
   python3 -m venv ally_env
   source ally_env/bin/activate
   ```

2. Update `pip` and install dependencies:

   For both Linux and Windows:

   ```bash
   pip install -U pip
   pip install -r requirements.txt
   ```

   (Upgrade the pip if neccessary)

### Configure Environment Variables

1. Set up the following environment variables in a `.env` file in the project root directory:
   ```env
   LIVEKIT_URL=<your_livekit_url>
   LIVEKIT_API_KEY=<your_livekit_api_key>
   LIVEKIT_API_SECRET=<your_livekit_api_secret>
   DEEPGRAM_API_KEY=<your_deepgram_api_key>
   OPENAI_API_KEY=<your_openai_api_key>
   ELEVEN_API_KEY=<your_eleven_api_key>
   GROQ_API_KEY=<your_groq_api_key>
   ```
   (get the credentials for the Livekit informations by creating a free account in Livekit)

2. **Groq API Key**: Obtain this key from your Groq account after signup.

3. **LiveKit Details**: Generate the URL, API key, and secret from your LiveKit dashboard.

4. Extract the remaining keys (DeepGram, OpenAI, Eleven Labs) from the password-protected zip file sent via email.

---

## Running the Solution

### Download Required Files

1. Download all required models and assets:

   For Windows:

   ```bash
   python main.py download-files
   ```

   For Linux:

   ```bash
   python3 main.py download-files
   ```

### Start the Assistant

1. For production:

   For Windows:
   
   ```bash
   python main.py start
   ```

   For Linux:

   ```bash
   python3 main.py start
   ```

2. Once the assistant is running, connect it to the hosted [Livekit Playground](https://agents-playground.livekit.io/) for testing. (make sure you have an account on Livekit)

Certainly! Adding a **File Structure** section in the README is a great way to help users navigate the repository. Here's how you can include it:

---

## File Structure

The following is an overview of the directory structure and the purpose of each file/folder:

```plaintext
├── main.py          # Main script to initialize and start the assistant.
├── initialization.py     # Configuration functions to start the system 
├── assistant.py # Contains the AssistantFunction class 
├── video_processing.py    # Contains functions to handle video processing tasks.
├── groq_open.py           # Contains the Groq_Open_LLM() class.
├── requirements.txt      # Python dependencies required to run the project.
├── README.md             # Documentation for the project.
├── .env (should be created by the user)  # Environment variables (API keys).
├── images/                # Contains images for the README. file.
│   ├── pic1.png
│   ├── pic2.png
│   └── ...
```

### Key Components

- **`main.py`**: The entry point for running the assistant. Includes functions for initialization and starting the assistant.
- **`assistant.py`**: AssistantFunction Class wherein additional methods have be added for function calling when a person is there in the frame.
- **`video_processing.py`**: Manages the processing of frame when the webcam is enabled for vision realated tasks.
- **`groq_open.py`**: Contains the class for setting up the open source Groq model and structuring of it's responses.
- **`requirements.txt`**: Lists all Python packages required to set up the project environment.

---

## Architecture and Flow

### Flow
 My code defines a real-time assistant that connects to a LiveKit room, initializes necessary components like GPT and Open LLM (Groq), and handles user interactions through messages or video frames. The assistant listens for user input, processes it, and determines the appropriate response. If the input involves vision-based tasks (like detecting a person in the frame), the assistant invokes specific functions (e.g., `image` or `person_in_frame`) to handle the request. These functions, defined using LiveKit's `llm.FunctionContext`, ensure that vision-related user queries are processed accurately and trigger appropriate logic based on the user's message.

 Here when a user asks for clarification `about a person or the user himself (user included here for testing in the livekit playground) accurately and in good detail` then the person_in_frame function gets called and subsquent response is obatined using the groq model.
  
 A pictorially understanding of all possible cases is shown in the figure below:
 ![Alt Text](images/pic2.png)

I have also added yolov5-object-detection algortihm in the branch named `yolo` wherein we get a more robust person detection infuding both the capabilities of function calling targtted object(person) detection algorithm. This can also be converted into only using the object detection algorithm to save on latency, but the algoroithm must be called everytime a person is in frame which may consume more energy.

## Additional Modifications (Opitional)

### Chaning the Open Source Model
 As mentioned eariler I use the **Groq LLaMA 3.2-11B Vision Preview** model for person based detection and decriptions. Using the same grok api we can also choose the more powerful model **Groq LLaMA 3.2-90B Vision Preview**, which use 90B paramter. This can be done by modifiying the `initialization.py` file in the `Initialization` class under the method `setting_open_llm()` from `"llama-3.2-11b-vision-preview"` to `"llama-3.2-90b-vision-preview"`. 

 ![Alt Text](images/pic1.png)

### Removing Print Statement

   I have kept the print statements which were present as the part of the baseline code, but they can be removed for some improvement in speed.

---
## Examples:

### Baseline

As seen in the baseline the `gpt-4o` is not able to describe the person.  
![Alt Text](images/baseline.png)
### My Implementation
![Alt Text](images/my_implementation.png)
![Alt Text](images/my_implementation3.png)
As you can see from the figure above, the open source LLM model (`grok`) is able to describe the person in frame. Another example of an object (smartphone) is shown below whose response is given by the `gpt-40`. This can also be checked form the logs while running this reposistory.

![Alt Text](images/my_implementation2.png)

---

## Challenges Encountered

- **Limited Availability of Open Source LLMs**:
  - There were few open-source LLMs that were OpenAI-compatible within the LiveKit framework and also supported vision. I found **LLaVA**, which works within the Ollama framework but needed to be run locally.
  - I opted for the **Groq Cloud Models**, where the **Groq LLaMA 3.2-11B Vision Preview** and **Groq LLaMA 3.2-90B Vision Preview** were the only available vision options. However, these models were not compatible with the LiveKit framework.

- **Custom Compatibility Solution**:
  - To address this, I implemented a separate class, `Groq_Open_LLM`, in the file `groq_open.py`. This class was designed to manually structure the output for compatibility with the LiveKit framework.

---

## Troubleshooting

- **Environment Variables**:
  - Ensure all API keys are set correctly in the `.env` file. You need to create this file and add in all the keys as shown eariler.
  - Double-check the password for extracting keys from the zip file.

- **Latency Issues**:
  - Verify that your GPU is optimized for the person-detection model.
  - Check network latency for Groq API calls.

- **API Errors**:
  - Confirm API key validity and ensure your subscription allows necessary API calls.

---

