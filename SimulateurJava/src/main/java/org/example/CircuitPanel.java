package org.example;

import javax.swing.*;
import javax.swing.Timer;
import java.awt.*;
import java.io.*;
import java.net.*;
import java.util.*;
import java.util.List;
import org.json.JSONArray;

public class CircuitPanel extends JPanel {
    public java.util.List<Element> elements;
    private Robot robot;
    public Map<String, Integer> stationCharges;
    private Timer animationTimer;
    private int robotTargetIndex = -1;
    private String blocActuel = null;

    private enum RobotState { IDLE, GOING_TO_BLOCK, GOING_TO_STATION }
    private RobotState robotState = RobotState.IDLE;
    private boolean sensHoraire = true;
    private JTextArea actionLog;
    private Set<String> blocsRecuperes = new HashSet<>();
    private final UUID robotUuid;

    private static final Map<Integer, String> INT_TO_BLOC = Map.of(
            2, "Bloc jaune",
            3, "Bloc rouge",
            6, "Bloc rose",
            7, "Bloc violet",
            10, "Bloc vert"
    );

    private String nomBlocDepuisId(int id) {
        return switch (id) {
            case 2 -> "Bloc jaune";
            case 3 -> "Bloc rouge";
            case 6 -> "Bloc rose";
            case 7 -> "Bloc violet";
            case 10 -> "Bloc vert";
            default -> null;
        };
    }

    public CircuitPanel(Robot robot) {
        this.robot = robot;
        this.robotUuid = robot.getUuid();
        this.stationCharges = new HashMap<>();
        stationCharges.put("Station 1", 0);
        stationCharges.put("Station 2", 0);
        initElements();

        // Initialisation du log
        actionLog = new JTextArea(10, 30);
        actionLog.setEditable(false);
        actionLog.setLineWrap(true);
        actionLog.setWrapStyleWord(true);

        animationTimer = new Timer(400, e -> animateRobot());
        animationTimer.start();
    }

    public JTextArea getActionLog() {
        return actionLog;
    }

    private void initElements() {
        elements = new ArrayList<>();
        elements.add(new Element("Départ", false, false, Color.LIGHT_GRAY));
        elements.add(new Element("Bloc jaune", true, false, Color.YELLOW));
        elements.add(new Element("Bloc rouge", true, false, Color.RED));
        elements.add(new Element("Station 1", false, true, Color.LIGHT_GRAY));
        elements.add(new Element("Bloc rose", true, false, Color.PINK));
        elements.add(new Element("Bloc violet", true, false, new Color(128, 0, 128)));
        elements.add(new Element("Station 2", false, true, Color.LIGHT_GRAY));
        elements.add(new Element("Bloc vert", true, false, Color.GREEN));

        blocsRecuperes.clear();
        robot.setPosition(0);
    }

    public void reset() {
        initElements();
        stationCharges.put("Station 1", 0);
        stationCharges.put("Station 2", 0);
        robot.setPosition(0);
        robotState = RobotState.IDLE;
        robotTargetIndex = -1;
        blocActuel = null;
        actionLog.setText(""); // Réinitialiser le log
        repaint();
    }

    public void goToBloc(String nomBloc) {
        if (blocsRecuperes.contains(nomBloc)) {
            actionLog.append("❌ Le " + nomBloc.toLowerCase() + " a déjà été ramassé !\n");
            return;
        }

        for (int i = 0; i < elements.size(); i++) {
            if (elements.get(i).nom.equals(nomBloc)) {
                blocActuel = nomBloc;
                robotTargetIndex = i;
                robotState = RobotState.GOING_TO_BLOCK;
                calculerSens(robot.getPosition(), robotTargetIndex);
                actionLog.append("Se dirige vers " + nomBloc.toLowerCase() + "\n");
                return;
            }
        }

        actionLog.append("❓ Bloc \"" + nomBloc + "\" introuvable.\n");
    }

    private void calculerSens(int depart, int cible) {
        int n = elements.size();
        int sensDirect = (cible - depart + n) % n;
        int sensInverse = (depart - cible + n) % n;
        sensHoraire = sensDirect <= sensInverse;
    }

    private void animateRobot() {
        if (robotTargetIndex != -1) {
            if (robot.getPosition() != robotTargetIndex) {
                int pos = robot.getPosition();
                if (sensHoraire)
                    robot.setPosition((pos + 1) % elements.size());
                else
                    robot.setPosition((pos - 1 + elements.size()) % elements.size());
                repaint();
            } else {
                if (robotState == RobotState.GOING_TO_BLOCK) {
                    elements.get(robotTargetIndex).couleur = Color.LIGHT_GRAY;
                    blocsRecuperes.add(blocActuel);
                    actionLog.append("Ramasse le " + blocActuel.toLowerCase() + "\n");

                    String stationNom = robot.choisirStation(blocActuel, stationCharges);
                    for (int j = 0; j < elements.size(); j++) {
                        if (elements.get(j).nom.equals(stationNom)) {
                            robotTargetIndex = j;
                            robotState = RobotState.GOING_TO_STATION;
                            calculerSens(robot.getPosition(), robotTargetIndex);
                            actionLog.append("Se dirige vers " + stationNom.toLowerCase() + "\n");
                            return;
                        }
                    }
                } else if (robotState == RobotState.GOING_TO_STATION) {
                    elements.get(robotTargetIndex).couleur = Color.GRAY;
                    stationCharges.put(elements.get(robotTargetIndex).nom,
                            stationCharges.get(elements.get(robotTargetIndex).nom) + 1);

                    actionLog.append("Dépose le " + (blocActuel != null ? blocActuel.toLowerCase() : "bloc")
                            + " dans " + elements.get(robotTargetIndex).nom.toLowerCase() + "\n");

                    robotTargetIndex = -1;
                    robotState = RobotState.IDLE;
                }
                repaint();
            }
        }
    }

    @Override
    protected void paintComponent(Graphics g) {
        super.paintComponent(g);
        Graphics2D g2 = (Graphics2D) g;
        g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
        int centerX = getWidth() / 2;
        int centerY = getHeight() / 2;
        int radius = 250;
        int size = 100;

        for (int i = 0; i < elements.size(); i++) {
            double angle = 2 * Math.PI * i / elements.size();
            int x = (int) (centerX + radius * Math.cos(angle)) - size / 2;
            int y = (int) (centerY + radius * Math.sin(angle)) - size / 2;

            elements.get(i).x = x;
            elements.get(i).y = y;

            g2.setColor(elements.get(i).couleur);
            g2.fillOval(x, y, size, size);
            g2.setColor(Color.DARK_GRAY);
            g2.setStroke(new BasicStroke(2));
            g2.drawOval(x, y, size, size);

            g2.setColor(Color.BLACK);
            Font font = new Font("SansSerif", Font.PLAIN, 12);
            g2.setFont(font);
            FontMetrics fm = g2.getFontMetrics();

            String nom = elements.get(i).nom;

            // Si c’est une station, afficher aussi la charge
            if (nom.startsWith("Station")) {
                int charge = stationCharges.getOrDefault(nom, 0);
                String ligne1 = nom + " :";
                String ligne2 = charge + " bloc" + (charge > 1 ? "s" : "");

                int text1Width = fm.stringWidth(ligne1);
                int text2Width = fm.stringWidth(ligne2);
                int textHeight = fm.getAscent();

                int textX1 = x + (size - text1Width) / 2;
                int textX2 = x + (size - text2Width) / 2;

                int totalHeight = textHeight * 2 + 4; // 4 px d'espacement entre les lignes
                int startY = y + (size - totalHeight) / 2 + textHeight;

                g2.drawString(ligne1, textX1, startY);
                g2.drawString(ligne2, textX2, startY + textHeight + 4);

            } else {
                // Sinon, juste le nom de l’élément centré
                int textWidth = fm.stringWidth(nom);
                int textHeight = fm.getAscent();
                g2.drawString(nom, x + (size - textWidth) / 2, y + (size + textHeight) / 2 - 4);
            }

        }

        // Dessiner le robot
        int robotIndex = robot.getPosition();
        Element e = elements.get(robotIndex);
        g2.setColor(Color.BLUE);
        int robotSize = size / 3;
        g2.fillOval(e.x + (size - robotSize) / 2, e.y + (size - robotSize) / 2, robotSize, robotSize);
    }

    public List<String> fetchOrdresDepuisServeur() {
        List<String> blocsARecuperer = new ArrayList<>();
        List<Integer> codes = NetworkUtils.fetchInstructions(robotUuid);

        if (codes.isEmpty()) {
            actionLog.append("Aucun ordre reçu depuis le serveur.\n");
            return blocsARecuperer;
        }

        for (int code : codes) {
            String nomBloc = nomBlocDepuisId(code);
            if (nomBloc != null) {
                blocsARecuperer.add(nomBloc);
            } else {
                actionLog.append("❗ Code bloc inconnu : " + code + "\n");
            }
        }
        return blocsARecuperer;
    }

    public void executerOrdresDepuisServeur() {
        List<String> ordre = fetchOrdresDepuisServeur();
        if (ordre.isEmpty()) {
            actionLog.append("Aucun ordre valide reçu depuis le serveur.\n");
            return;
        }

        new Thread(() -> {
            for (String bloc : ordre) {
                try {
                    goToBloc(bloc);

                    while (robotState != RobotState.IDLE || robotTargetIndex != -1) {
                        Thread.sleep(200);
                    }
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        }).start();
    }

}