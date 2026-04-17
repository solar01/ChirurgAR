import queue
import sounddevice as sd
import json
import socket
from vosk import Model, KaldiRecognizer

MODEL_PATH = "vosk-model-small-pl-0.22"
SAMPLE_RATE = 44100
UDP_IP = "127.0.0.1"
UDP_PORT = 7777

# Słownik płaszczyzn
PLANES = {
    "osiowa": "axial", "osiowy": "axial", 
    "strzałkowa": "sagittal", "strzałkowy": "sagittal", "strzałkowe": "sagittal", "strzałkowo": "sagittal",
    "czołowa": "coronal", "czołowy": "coronal", "czołowo": "coronal", "czołowe": "coronal",
}

# Słownik akcji 
ACTIONS = {
    "następna": "next_slice","następną": "next_slice", "następne": "next_slice", "kolejna": "next_slice", "kolejne": "next_slice",
    "poprzednia": "prev_slice", "poprzednią": "prev_slice", "poprzednie": "prev_slice", "cofnij": "prev_slice",
    "przybliż": "zoom_in", "oddal": "zoom_out",
    "reset": "reset_view",
    "lewo": "pan_left", "prawo": "pan_right",
    "góra": "pan_up", "dół": "pan_down",
    # KOMENDY DO LANDMARKÓW:
    "zostaw": "focus_plane", "zostać": "focus_plane",
    "pokaż": "show_landmark", "wyświetl": "show_landmark",
    "ukryj": "hide_landmark", "schowaj": "hide_landmark",
    "zakończ": "exit"
}

# Słownik pomocniczy do wyłapywania liczb 
NUMBERS = {
    "jeden": 1, "pięć": 5,
    "dziesięć": 10, "dwadzieścia": 20}

q = queue.Queue()
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Wysyłanie komendy w formie json
def send_command(plane, action, label, value=1):
    data = {
        "plane": plane,
        "action": action,
        "value": value,
        "label": label
    }
    message = json.dumps(data)
    sock.sendto(bytes(message, "utf-8"), (UDP_IP, UDP_PORT))
    print(f">>> Wysłano: {message}")

def map_command(text):
    text = text.lower()
    words = text.split()
    detected_plane = "global"
    detected_action = None
    detected_value = 1
    detected_label = None 

    for word, plane_id in PLANES.items():
        if word in text:
            detected_plane = plane_id
            break

    # Szukamy akcji 
    for i, word in enumerate(words):
        # Sprawdzamy, czy słowo jest w ACTIONS
        for action_word, action_id in ACTIONS.items():
            if action_word in word:
                detected_action = action_id
                
                # Jeśli akcja to pokazanie/ukrycie, 
                # weź następne słowo jako nazwę landmarku
                if action_id in ["show_landmark", "hide_landmark"]:
                    if i + 1 < len(words):
                        detected_label = words[i+1]
                break
        if detected_action: break

    # Szukamy wartości liczbowej (słownie)
    for word, number in NUMBERS.items():
        if word in text:
            detected_value = number
            break
    
    # Sprawdzamy surowe cyfry 
    for word in words:
        if word.isdigit():
            detected_value = int(word)

    return detected_plane, detected_action, detected_value, detected_label

def audio_callback(indata, frames, time, status):
    if status: print(status)
    q.put(bytes(indata))

print("Ładowanie modelu...")
model = Model(MODEL_PATH)
recognizer = KaldiRecognizer(model, SAMPLE_RATE)
print("Nasłuchiwanie (np. 'nastepna o pięć', 'góra o dziesięć', 'prawo')")

with sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=8000, dtype='int16',
                       channels=1, callback=audio_callback):

    while True:
        data = q.get()
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get("text", "")

            if text:
                plane, action, value, label = map_command(text)
                print(f"Usłyszano: '{text}' | Rozpoznano: płaszczyzna={plane}, akcja={action}, wartość={value}")

                if action == "exit":
                    send_command(plane, action, label, value)
                    break
                
                if action:
                    send_command(plane, action, label, value)

sock.close()