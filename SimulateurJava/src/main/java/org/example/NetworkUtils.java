package org.example;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

public class NetworkUtils {

    public static List<Integer> fetchInstructions(UUID robotUuid) {
        List<Integer> instructions = new ArrayList<>();
        try {
            URL url = new URL("http://10.7.5.118:8000/get_instructions?robot_id=" + robotUuid);
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();

            conn.setRequestMethod("GET");
            conn.setRequestProperty("Accept", "application/json");

            int responseCode = conn.getResponseCode();
            System.out.println(responseCode);
            System.out.println(conn.getResponseMessage());

            // Lire la réponse
            if (conn.getResponseCode() == 200) {
                try (BufferedReader br = new BufferedReader(
                        new InputStreamReader(conn.getInputStream(), StandardCharsets.UTF_8))) {

                    StringBuilder response = new StringBuilder();
                    String line;
                    while ((line = br.readLine()) != null) {
                        response.append(line.trim());
                    }

                    // Exemple de réponse attendue : [2,6,7]
                    JSONObject jsonObject = new JSONObject(response.toString());
                    JSONArray array = jsonObject.getJSONArray("blocks");
                    System.out.println(array);

                    for (int i = 0; i < array.length(); i++) {
                        instructions.add(array.getInt(i));
                    }
                }
            } else {
                System.err.println("❌ Erreur serveur : " + conn.getResponseCode());
            }
        } catch (Exception e) {
            System.err.println("❌ Exception réseau : " + e.getMessage());
        }
        return instructions;
    }
}