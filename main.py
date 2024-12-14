import asyncio
from dotenv import load_dotenv
from livekit import agents, rtc
from livekit.agents import JobContext, WorkerOptions, cli
from livekit.agents.llm import (
    ChatContext,
    ChatImage,
    ChatMessage,
)
from initialization import Initialization
from video_processing import _getVideoFrame

load_dotenv() # Loading environement variables

    
async def entrypoint(ctx: JobContext):

#------------------------------------------------------CONNECTING TO THE ROOM---------------------------------------------#
    await ctx.connect()  
    print(f"Room name: {ctx.room.name}")
    

#------------------------------------------------------INITIALIZATIONS---------------------------------------------#
    init = Initialization(ctx)
    
    chat_context = init.setting_chat_context()
    gpt = init.setting_gpt()
    o_llm = init.setting_open_llm()
    assistant = init.setting_voice_assistant()
    chat = init.setting_chat_manager()


#------------------------------------------------------EVENTS HANDLERS------------------------------------------------------#
    
    async def _answer(text: str, use_image: bool = False, open_llm: bool = False):
        """
        Answer the user's message with the given text and optionally the latest
        image captured from the video track.
        """
        print(f"[LOG] _answer called with text: {text}, use_image: {use_image}, open_llm: {open_llm}")
        try:
            
            if use_image:
                print("[LOG] Getting video frame")
                content: list[str | ChatImage] = [text]
                latest_image = await _getVideoFrame(ctx, assistant)

                if latest_image is not None:

                    print("[LOG] Adding image to content")
                    content.append(ChatImage(image=latest_image))

                    if open_llm:

                        print("[LOG] Getting open LLM response")
                        response = o_llm.chat(ChatImage(image=latest_image),text)
                        content: list[str | ChatImage] = ['Repeat this- ' + response]

                else:
                    print("[LOG] No image available")


            print("[LOG] Adding full message to chat context")
            chat_context.messages.append(ChatMessage(role="user", content=content))  
            print("[LOG] Getting GPT response")
            stream = gpt.chat(chat_ctx=chat_context)

            print("[LOG] Sending response to assistant")
            await assistant.say(stream, allow_interruptions=True)

        except Exception as e:
            print(f"[ERROR] Error in _answer: {e}")


    @chat.on("message_received")
    def on_message_received(msg: rtc.ChatMessage):
        """This event triggers whenever we get a new message from the user."""

        if msg.message:
            asyncio.create_task(_answer(msg.message, use_image=False))


    @assistant.on("function_calls_finished")  # This is trigerred everytime after a function from the assistant class is called. 
    def on_function_calls_finished(called_functions: list[agents.llm.CalledFunction]):
        """This event triggers when an assistant's function call completes."""
        print(f"[LOG] Function calls finished. Number of calls: {len(called_functions)}")
    
        if len(called_functions) == 0:
            print("[LOG] No functions were called")
            return
    
        try:
            person_in_frame_called = any(
            func.call_info.function_info.name == "person_in_frame"
            for func in called_functions
            )

            user_msg = called_functions[0].call_info.arguments.get("user_msg")  # Now the user_msg variable has the value that the user promped which needed vision capabilites 
            print(f"[LOG] Function call user message: {user_msg}")
            
            if user_msg:
                if person_in_frame_called:
                    print("[LOG] Creating task for _answer with image and person")
                    asyncio.create_task(_answer(user_msg, use_image=True,open_llm=True))
                else:
                    print("[LOG] Creating task for _answer with image")
                    asyncio.create_task(_answer(user_msg, use_image=True,open_llm=False))
            else:
                print("[LOG] No user message to process")
        except Exception as e:
            print(f"[ERROR] Error in function calls handler: {e}")


#------------------------------------------------------START--------------------------------------------------------#
    assistant.start(ctx.room) # Assistant starts listening the room
    await asyncio.sleep(1) # Breathing time for the system
    await assistant.say("Hi there! How can I help?", allow_interruptions=True) #Start with a greeting
#-------------------------------------------------------------------------------------------------------------------#

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))