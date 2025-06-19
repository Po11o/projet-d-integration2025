from time import sleep, ticks_ms, ticks_diff
from machine import Pin, PWM
from motor_driver import DCMotor
from capteur_ligne import LineSensor
from reseau import envoyer_telemetrie
from ultrason import Ultrason

VITESSE_SUIVI_LIGNE = 70
VITESSE_CORRECTION = 50

Ultrason_comp = Ultrason(22, 23)

in1 = Pin(14, Pin.OUT)
in2 = Pin(12, Pin.OUT)
in3 = Pin(13, Pin.OUT)
in4 = Pin(27, Pin.OUT)

enable_pwm_left = PWM(Pin(25), freq=1000)
enable_pwm_right = PWM(Pin(26), freq=1000)

right_motor = DCMotor(in1, in2, enable_pwm_right)
left_motor = DCMotor(in3, in4, enable_pwm_left)

suiveur_gauche = LineSensor(19)
suiveur_droite = LineSensor(18)

ligne_actuelle = 1
sens_horaire = True

def save_ligne_actuelle(value):
    try:
        with open('ligne_actuelle.txt', 'w') as f:
            f.write(str(value))
    except Exception as e:
        print("Error saving line:", e)

def load_ligne_actuelle():
    try:
        with open('ligne_actuelle.txt', 'r') as f:
            return int(f.read())
    except:
        return 1

def reset_ligne_actuelle():
    global ligne_actuelle
    ligne_actuelle = 1
    save_ligne_actuelle(ligne_actuelle)

def stop():
    left_motor.stop()
    right_motor.stop()

def avancer():
    left_motor.forward(VITESSE_SUIVI_LIGNE)
    right_motor.forward(VITESSE_SUIVI_LIGNE)

def turn_left():
    left_motor.forward(VITESSE_CORRECTION)
    right_motor.backwards(VITESSE_CORRECTION)
   

def turn_right():
    left_motor.backwards(VITESSE_CORRECTION)
    right_motor.forward(VITESSE_CORRECTION)
    

def etat_suiveur():
    gauche = suiveur_gauche.line_detected()
    droite = suiveur_droite.line_detected()

    if gauche and droite:
        return "LIGNE"    # Both sensors detect line â crossed line
    elif gauche:
        return "GAUCHE"   # Left sensor detects line â turn left
    elif droite:
        return "DROITE"   # Right sensor detects line â turn right
    else:
        return "AVANCER"  # No sensor detects line â go forward

def suivre_ligne(ligne_cible):
    global ligne_actuelle, sens_horaire

    compteur = ligne_actuelle
    ligne_detectee = False
    derniere_detection = ticks_ms()
    derniere_telemetrie = ticks_ms()

    print(f"ð Navigating: current={ligne_actuelle} â target={ligne_cible}")

    while compteur != ligne_cible:
        now = ticks_ms()
        etat = etat_suiveur()

        # Envoyer la tÃ©lÃ©metrie toutes les 1s
        if ticks_diff(now, derniere_telemetrie) >= 1000:
            envoyer_telemetrie(
                ultrason_distance=Ultrason_comp.distance_cm(),
                ligne=compteur,
                vitesse=VITESSE_SUIVI_LIGNE,
                statut="MOVING",
                pince_active=False
            )
            derniere_telemetrie = now

        # DÃ©tection de ligne traversÃ©e (double capteur)
        if etat == "LIGNE" and not ligne_detectee:
            compteur = compteur + 1 if sens_horaire else compteur - 1
            compteur = (compteur - 1) % 10 + 1  # wrap 1..10
            ligne_detectee = True
            print(f"â Line crossed, count = {compteur}")
            stop()
            sleep(0.2)  # Court arrÃªt pour fiabilitÃ©
        elif etat != "LIGNE":
            ligne_detectee = False  # prÃªt Ã  dÃ©tecter prochaine ligne

        # Mouvement principal basÃ© sur les capteurs
        if etat == "AVANCER":
            avancer()

        elif etat == "GAUCHE":
            print("âªï¸ Correction gauche")
            turn_left()
            sleep(0.05)

        elif etat == "DROITE":
            print("â©ï¸ Correction droite")
            turn_right()
            sleep(0.05)

        else:
            # SÃ©curitÃ© par dÃ©faut
            avancer()

        sleep(0.01)

    ligne_actuelle = compteur
    save_ligne_actuelle(ligne_actuelle)
    stop()

    # TÃ©lÃ©metrie finale
    envoyer_telemetrie(
        ultrason_distance=Ultrason_comp.distance_cm(),
        ligne=ligne_actuelle,
        vitesse=0,
        statut="STOP",
        pince_active=False
    )

    print("ð Arrived at line", ligne_actuelle)


def executer_mission_par_ligne(ligne_recue):
    print(f"ð§­ Moving to line: {ligne_recue}")
    suivre_ligne(ligne_recue)
