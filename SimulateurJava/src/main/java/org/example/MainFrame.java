package org.example;

import javax.swing.*;
import java.awt.*;

public class MainFrame extends JFrame {
    private CircuitPanel circuitPanel;
    private ControlPanel controlPanel;
    private Robot robot;

    public MainFrame() {
        super("Simulateur de Robot");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setSize(1200, 800);
        setLayout(new BorderLayout());

        robot = new Robot();
        circuitPanel = new CircuitPanel(robot);
        controlPanel = new ControlPanel(circuitPanel, robot);

        // Ajout du panneau de log dans un JScrollPane
        JTextArea actionLog = circuitPanel.getActionLog();
        JScrollPane logScrollPane = new JScrollPane(actionLog);
        logScrollPane.setPreferredSize(new Dimension(300, 0));
        logScrollPane.setBorder(BorderFactory.createTitledBorder("Actions du robot"));

        // Scroll automatique en bas à chaque ajout de texte
        actionLog.setCaretPosition(actionLog.getDocument().getLength());

        add(circuitPanel, BorderLayout.CENTER);
        add(controlPanel, BorderLayout.SOUTH);
        add(logScrollPane, BorderLayout.EAST); // Ajout du log à droite

        setVisible(true);
    }
}