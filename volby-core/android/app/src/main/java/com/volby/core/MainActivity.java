package com.volby.core;

import android.app.Activity;
import android.os.Bundle;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.TextView;

import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLEncoder;

public class MainActivity extends Activity {

    private static final String API_URL =
        "https://volby-core-api.onrender.com/chat";

    private TextView responseText;
    private EditText input;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        LinearLayout layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.VERTICAL);
        layout.setPadding(32, 32, 32, 32);

        TextView title = new TextView(this);
        title.setText("Volby Core");
        title.setTextSize(28);

        input = new EditText(this);
        input.setHint("Enter a command");

        Button send = new Button(this);
        send.setText("Send");

        responseText = new TextView(this);
        responseText.setText("Connected to Volby Core Android.");
        responseText.setTextSize(18);

        layout.addView(title);
        layout.addView(input);
        layout.addView(send);
        layout.addView(responseText);

        setContentView(layout);

        send.setOnClickListener(v -> sendMessage());
    }

    private void sendMessage() {
        String message = input.getText().toString().trim();

        if (message.isEmpty()) {
            responseText.setText("Enter a command first.");
            return;
        }

        responseText.setText("Thinking...");

        new Thread(() -> {
            try {
                String encoded =
                        URLEncoder.encode(message, "UTF-8");

                URL url = new URL(API_URL + "?message=" + encoded);

                HttpURLConnection connection =
                        (HttpURLConnection) url.openConnection();

                connection.setRequestMethod("POST");
                connection.setConnectTimeout(10000);
                connection.setReadTimeout(15000);

                BufferedReader reader =
                        new BufferedReader(
                                new InputStreamReader(
                                        connection.getInputStream()
                                )
                        );

                StringBuilder result = new StringBuilder();
                String line;

                while ((line = reader.readLine()) != null) {
                    result.append(line);
                }

                reader.close();
                connection.disconnect();

                JSONObject json = new JSONObject(result.toString());
                String response = json.getString("response");

                runOnUiThread(() ->
                        responseText.setText(response)
                );

            } catch (Exception e) {
                runOnUiThread(() ->
                        responseText.setText(
                                "Connection error:\n" + e.getMessage()
                        )
                );
            }
        }).start();
    }
}