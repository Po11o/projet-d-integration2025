import network
import urequests
import json
from time import sleep

# ➤ Connect to Wi-Fi
def connecter_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("🔌 Connexion Wi-Fi...")
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            print(".", end="")
            sleep(0.5)
    print("\n✅ Connecté avec IP :", wlan.ifconfig()[0])

# ➤ Send telemetry data to server
def envoyer_telemetrie(robot_id="255f30bc-46f7-41d4-ba1d-db76a0afd7f7", ligne=False, vitesse=0, statut="STOP", pince_active=False):
    url = "http://10.7.5.119:8000/telemetry"
    data = {
        "robot_id": robot_id,
        "vitesse": vitesse,
        "distance_ultrasons": 0.0,  # You can update this before calling if needed
        "statut_deplacement": statut,
        "ligne": ligne,
        "pince_active": pince_active
    }
    try:
        res = urequests.post(url, json=data)
        print("📡 Télémetrie envoyée :", res.status_code)
        res.close()
    except Exception as e:
        print("❌ Erreur télémétrie :", e)

# ➤ Get instructions from server
def recuperer_instruction(robot_id="255f30bc-46f7-41d4-ba1d-db76a0afd7f7"):
    url = f"http://10.7.5.119:8000/instructions?robot_id={robot_id}"
    try:
        res = urequests.get(url)
        if res.status_code == 200:
            data = res.json()
            print("📥 Instruction reçue :", data)
            res.close()
            return data
        else:
            print("⚠️ Mauvaise réponse :", res.status_code)
    except Exception as e:
        print("❌ Erreur GET :", e)
    return None

# ➤ Send mission summary
def envoyer_summary(robot_id="255f30bc-46f7-41d4-ba1d-db76a0afd7f7"):
    url = "http://10.7.5.119:8000/summary"
    data = {
        "robot_id": robot_id
    }
    try:
        res = urequests.post(url, json=data)
        print("✅ Résumé de mission envoyé :", res.status_code)
        res.close()
    except Exception as e:
        print("❌ Erreur envoi résumé :", e)
