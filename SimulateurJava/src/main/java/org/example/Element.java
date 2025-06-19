package org.example;

import java.awt.*;

public class Element {
    public String nom;
    public boolean estBloc;
    public boolean estStation;
    public Color couleur;
    public int x, y;

    public Element(String nom, boolean estBloc, boolean estStation, Color couleur) {
        this.nom = nom;
        this.estBloc = estBloc;
        this.estStation = estStation;
        this.couleur = couleur;
    }
}