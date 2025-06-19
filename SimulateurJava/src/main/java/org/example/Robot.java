package org.example;

import java.util.*;

public class Robot {
    private int position;
    private final UUID uuid;

    public Robot() {
        this.position = 0;
        this.uuid = UUID.randomUUID(); // Génère un UUID unique au robot
    }

    public void setPosition(int pos) { this.position = pos; }
    public int getPosition() { return position; }
    public UUID getUuid() { return uuid; }

    public String choisirStation(String nomBloc, Map<String, Integer> stationCharges) {
        switch (nomBloc) {
            case "Bloc violet":
            case "Bloc vert":
                return "Station 2";
            case "Bloc jaune":
                int s1 = stationCharges.get("Station 1");
                int s2 = stationCharges.get("Station 2");
                if (s1 < s2) return "Station 1";
                if (s2 < s1) return "Station 2";
                return Math.random() < 0.5 ? "Station 1" : "Station 2";
            default:
                return "Station 1";
        }
    }
}