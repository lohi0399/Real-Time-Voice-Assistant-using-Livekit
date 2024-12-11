from livekit.agents import llm
from typing import Annotated
import logging

class AssistantFunction(llm.FunctionContext):
    """This class is used to define functions that will be called by the assistant."""

    @llm.ai_callable(
        description=(
            "Called when asked to evaluate something that would require vision capabilities"
        )
    )

    async def image(
        self,
        user_msg: Annotated[
            str,
            llm.TypeInfo(
                description="The user message that triggered this function"
            ),
        ],
    ):
        print(f"[LOG] Message triggering vision capabilities: {user_msg}")

        return None
