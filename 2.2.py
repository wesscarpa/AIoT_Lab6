import asyncio
import random
import ToDo1
from google import genai
from dotenv import load_dotenv
from torch.utils.data import Dataset, DataLoader
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
    data_dir = r"human+activity+recognition+using+smartphones\UCI HAR Dataset\UCI HAR Dataset"
    ds = ToDo1.UCIHARSignals(data_dir, "train")

    sample_idx = random.randint(0, len(ds)-1)

    x, y, y_name = ds[sample_idx] # select specific sample to test LLM prompt

    #print(x)
    direct_response_template = """
        Device: Smartphone
        Attached Location: {location}
        Candidate Activities: {activities}
        Data (Accelerometer X,Y,Z over time): X: {x_data}, Y: {y_data}, Z: {z_data}
        Question: Question: Which activity is being performed? Answer with exactly one candidate activity name and nothing else.
    """
    direct_response_prompt = direct_response_template.format(
        location = "Waist", 
        activities = ["WALKING", "WALKING_UPSTAIRS", "WALKING_DOWNSTAIRS", 
                        "SITTING", "STANDING", "LAYING"], 
        x_data = x[0][0:10],
        y_data = x[1][0:10], 
        z_data = x[2][0:10]
    )

    CoT_response_template = """
        Device: Smartphone
        Attached Location: {location}
        Candidate Activities: {activities}
        Data (Accelerometer X,Y,Z over time): X: {x_data}, Y: {y_data}, Z: {z_data}
        Question: Question: Which activity is being performed? Explain your reasoning step by step, then give the activity.
    """
    CoT_response_prompt = CoT_response_template.format(
           location = "Waist", 
        activities = ["WALKING", "WALKING_UPSTAIRS", "WALKING_DOWNSTAIRS", 
                        "SITTING", "STANDING", "LAYING"], 
        x_data = x[0],
        y_data = x[1], 
        z_data = x[2]
    ) 


    #Compare LLM response with ground truth label 
    print("CoT_LLM Response: ", asyncio.run(get_llm_response(CoT_response_prompt)))
    print("Direct_LLM Response: ", asyncio.run(get_llm_response(direct_response_prompt)))
    print("Ground Truth: ", y_name)