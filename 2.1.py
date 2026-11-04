import asyncio
import ToDo1
from google import genai
from dotenv import load_dotenv
import os

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_KEY")

async def get_llm_response(prompt):
    full_response = ""
    async with genai.Client(api_key=GEMINI_API_KEY).aio as client:
        async for partial in await client.models.generate_content_stream(
            model="gemini-3.5-flash-lite",
            contents=prompt,):
            if partial.text:
                full_response += partial.text
    return full_response    
        
if __name__ == "__main__":
    data = ToDo1.UCIHARSignals(r"human+activity+recognition+using+smartphones\UCI HAR Dataset\UCI HAR Dataset", "train")
    prompt = """
Device: Smartphone
Attached Location: {location}
Candidate Activities: {activities}
Data (Accelerometer X,Y,Z over time): {data}
Question: Which activity is being performed?
""", activities = ["WALKING", "WALKING_UPSTAIRS", "WALKING_DOWNSTAIRS", "SITTING", "STANDING", "LAYING"], data = 
    print(asyncio.run(get_llm_response(prompt)))