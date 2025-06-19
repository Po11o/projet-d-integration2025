# main.py
from time import sleep
from reseau import connecter_wifi, recuperer_instruction, envoyer_summary
from mission import executer_mission_par_ligne, reset_ligne_actuelle
from machine import Pin, PWM
from motor_driver import DCMotor
from capteur_ligne import LineSensor



def main():
    reset_ligne_actuelle()  # Reset current line to 1 on boot
    connecter_wifi("IMERIR Fablab", "imerir66")

    instruction = None
    while not instruction or "blocks" not in instruction or not instruction["blocks"]:
        print("ð Waiting for instructions from server...")
        instruction = recuperer_instruction()
        sleep(1)

    print("ð Instruction received:", instruction)

    for ligne in instruction["blocks"]:
        print(f"ð¯ Executing mission for line: {ligne}")
        executer_mission_par_ligne(ligne)
        sleep(1)  # Small delay between missions

    print("â Mission complete. Sending summary.")
    envoyer_summary()

# Call main() directly so it runs on boot
main()
#test_capteurs_et_moteurs()