# Envision-AI-Assignment-Solution-Lohit
This reposistory give the detailed solution to the assignment.

# Setup

First, create a virtual environment, update pip, and install the required packages:

```
$ python3 -m venv ally_env (for windows user you could use 'python' instead of 'python3')
$ source ally_env/bin/activate ( for windows user im the cmd use: .\ally_env\Scripts\activate.bat)
$ pip install -U pip
$ pip install -r requirements.txt
```

You need to set up the following environment variables:

First make a free account on livekit and get your own Livekit url, api key and secret.

Make sure you add the following lines by making a .env file within your project:

```
LIVEKIT_URL=...
LIVEKIT_API_KEY=...
LIVEKIT_API_SECRET=...
DEEPGRAM_API_KEY=...
OPENAI_API_KEY=...
ELEVEN_API_KEY=
```

Then, run the assistant:

```
$ python3 main.py download-files
$ python3 main.py start
or
$ python3 main.py dev
```

Finally, you can load the [hosted playground](https://agents-playground.livekit.io/) and connect it.

And most of all have fun with it :)
