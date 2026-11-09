
import network
import time
import urequests
import ujson

from IMU_capture import run_capture
import OLED
import time
import ntptime
import gc

# ==========================================
# CONFIGURATION
# ==========================================

WIFI_SSID = "Columbia University"
WIFI_PASSWORD = ""

GEMINI_API_KEY = "APIKEY"
MODEL = "gemini-3.5-flash-lite"

DATA_POINTS = 50


# ==========================================
# WIFI CONNECTION
# ==========================================

def connect_wifi():

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():

        print("Connecting to Wi-Fi...")

        wlan.connect(WIFI_SSID, WIFI_PASSWORD)

        timeout = 20

        while not wlan.isconnected() and timeout > 0:
            time.sleep(1)
            timeout -= 1

    if not wlan.isconnected():
        raise RuntimeError("Wi-Fi connection failed")

    print("Connected:", wlan.ifconfig())


# ==========================================
# GEMINI API REQUEST
# ==========================================

def ask_gemini(prompt, max_tokens):

    gc.collect()

    print("Free memory before request:", gc.mem_free())

    url = (
        "https://generativelanguage.googleapis.com/"
        "v1beta/models/" + MODEL + ":generateContent"
    )

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY
    }

    payload = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": max_tokens
        }
    }

    response = None
    result = None

    total_start = time.ticks_ms()

    # ==========================================
    # SEND REQUEST WITH RETRIES
    # ==========================================

    for attempt in range(5):

        try:

            gc.collect()

            print("Connecting to Gemini...")
            print("Sending request to Gemini...")
            print("Attempt:", attempt + 1)

            start = time.ticks_ms()

            response = urequests.post(
                url,
                headers=headers,
                data=ujson.dumps(payload)
            )

            elapsed = time.ticks_diff(
                time.ticks_ms(), start
            ) / 1000

            print("HTTP status:", response.status_code)
            print("Request completed in:", elapsed, "seconds")

            # ==========================================
            # READ RESPONSE
            # ==========================================

            result = response.json()

            if response.status_code != 200:

                print("API ERROR:")
                print(ujson.dumps(result))

                return "API ERROR"

            break

        except Exception as e:

            print("Gemini request failed:", repr(e))

            if response is not None:
                response.close()
                response = None

            if attempt == 4:

                print("All attempts failed.")
                return "REQUEST FAILED"

            print("Retrying in 5 seconds...")
            time.sleep(5)

        finally:

            if response is not None:
                response.close()
                response = None

    # ==========================================
    # PROCESS GEMINI RESPONSE
    # ==========================================

    try:

        if result is None:
            return "NO RESPONSE"

        if "candidates" not in result:

            print("No candidates returned:")
            print(ujson.dumps(result))

            return "NO RESPONSE"

        candidate = result["candidates"][0]

        print("Finish reason:", candidate.get("finishReason"))

        parts = candidate.get("content", {}).get("parts", [])

        if not parts:

            print("No response text returned.")
            return "NO RESPONSE"

        answer = parts[0].get("text", "")

        elapsed_total = time.ticks_diff(
            time.ticks_ms(), total_start
        ) / 1000

        print("Total elapsed time:", elapsed_total, "seconds")

        return answer.strip()

    except Exception as e:

        print("Response processing failed:", repr(e))

        return "RESPONSE ERROR"

    finally:

        gc.collect()

        print("Free memory after request:", gc.mem_free())

# ==========================================
# ORIGINAL PROMPTS
# ==========================================

CoT_response_template = """
You are an activity recognition assistant analyzing real-time IMU sensor data
collected by an ESP32. Here is the information about data you are going to receive and how to classify the activity from the data.
Assume the device is mounted so the z-axis is aligned upward while the person is standing.
Device: ESP32
Attached Location: {location}
Candidate Activities: {activities}
Data (Accelerometer X,Y,Z over time): X: {x_data}, Y: {y_data}, Z: {z_data}
Question: Which activity is being performed? Explain your reasoning step by step, then give the activity. Try to be concise to conserve tokens.
"""

direct_response_template = """
You are an activity recognition assistant analyzing real-time IMU sensor data
collected by an ESP32. Here is the information about data you are going to receive and how to classify the activity from the data.
Assume the device is mounted so the z-axis is aligned upward while the person is standing.
Device: ESP32
Attached Location: {location}
Candidate Activities: {activities}
Data (Accelerometer X,Y,Z over time): X: {x_data}, Y: {y_data}, Z: {z_data}
Question: Which activity is being performed? Answer with exactly one candidate activity name and nothing else.
"""


# ==========================================
# MAIN PROGRAM
# ==========================================

if __name__ == "__main__":
    
    
    print("BEGIN")
    ntptime.settime()

    print("TIME:", time.localtime())

    # Connect to Wi-Fi
    connect_wifi()

    # Capture accelerometer data
    print("Capturing accelerometer data...")

    ax, ay, az = run_capture()

    print("Capture complete.")

    # Candidate activities
    activities = [
        "WALKING",
        "WALKING_UPSTAIRS",
        "WALKING_DOWNSTAIRS",
        "SITTING",
        "STANDING",
        "LAYING"
    ]

    # Generate direct-response prompt
    direct_response_prompt = direct_response_template.format(
        location="Waist",
        activities=activities,
        x_data=ax[0:DATA_POINTS],
        y_data=ay[0:DATA_POINTS],
        z_data=az[0:DATA_POINTS]
    )

    # Generate chain-of-thought prompt
    CoT_response_prompt = CoT_response_template.format(
        location="Waist",
        activities=activities,
        x_data=ax[0:DATA_POINTS],
        y_data=ay[0:DATA_POINTS],
        z_data=az[0:DATA_POINTS]
    )
   

    
    print("Getting Direct Responce")
    Direct_response = ask_gemini(direct_response_prompt,64) 

    # Print results


    print("\nDirect_LLM Response:")
    print(Direct_response)
    
    OLED.display_text(Direct_response)
    
    
    print("Getting CoT Responce")
    CoT_response = ask_gemini(CoT_response_prompt, 1024)
    print("\nCoT_LLM Response:")
    print(CoT_response)
    

    # Display result on OLED

