# Envision-AI-Assignment-Solution-Lohit
This reposistory give the detailed solution to the assignment.

# Setup

First, create a virtual environment, update pip, and install the required packages:

```
$ python3 -m venv ally_env
$ source ally_env/bin/activate
$ pip install -U pip
$ pip install -r requirements.txt
```

You need to set up the following environment variables:

First make a free account on livekit and get your own Livekit url, api key and secret.
The other 3 api keys are in the password protected zip file, the password is in the email sent to you.

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
$ python3 assistant.py download-files
$ python3 assistant.py start
or
$ python3 assistant.py dev
```

Finally, you can load the [hosted playground](https://agents-playground.livekit.io/) and connect it.

And most of all have fun with it :)
