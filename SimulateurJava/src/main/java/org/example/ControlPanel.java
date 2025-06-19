package org.example;

import javax.swing.*;
import java.awt.*;

public class ControlPanel extends JPanel {
    public ControlPanel(CircuitPanel circuitPanel, Robot robot) {
        setLayout(new FlowLayout(FlowLayout.CENTER, 20, 10));
        setBackground(new Color(230, 230, 250));

        String[] blocs = {"Bloc jaune", "Bloc rouge", "Bloc rose", "Bloc violet", "Bloc vert"};
        JComboBox<String> blocSelector = new JComboBox<>(blocs);
        JButton goButton = new JButton("Aller chercher");
        JButton resetButton = new JButton("Réinitialiser");
        JButton serveurButton = new JButton("Exécuter via serveur");

        blocSelector.setFont(new Font("SansSerif", Font.PLAIN, 16));
        goButton.setFont(new Font("SansSerif", Font.BOLD, 16));
        resetButton.setFont(new Font("SansSerif", Font.BOLD, 16));
        serveurButton.setFont(new Font("SansSerif", Font.BOLD, 16));

        add(new JLabel("Choisissez un bloc : ")).setFont(new Font("SansSerif", Font.PLAIN, 16));
        add(blocSelector);
        add(goButton);
        add(resetButton);
        add(serveurButton);

        goButton.addActionListener(e -> {
            String selected = (String) blocSelector.getSelectedItem();
            circuitPanel.goToBloc(selected);
        });

        resetButton.addActionListener(e -> circuitPanel.reset());

        serveurButton.addActionListener(e -> circuitPanel.executerOrdresDepuisServeur());
    }
}