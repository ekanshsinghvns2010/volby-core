package com.volby.core;

import android.app.Activity;
import android.os.Bundle;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.TextView;

import com.volby.core.tools.AppLauncher;
import com.volby.core.tools.AppRegistry;

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

        LinearLayout layout =
                new LinearLayout(this);

        layout.setOrientation(
                LinearLayout.VERTICAL
        );

        layout.setPadding(
                32,
                32,
                32,
                32
        );

        TextView title =
                new TextView(this);

        title.setText("Volby Core");
        title.setTextSize(28);

        input =
                new EditText(this);

        input.setHint(
                "Tell Volby what you want to do"
        );

        Button send =
                new Button(this);

        send.setText("Send");

        responseText =
                new TextView(this);

        responseText.setText(
                "Connected to Volby Core Android."
        );

        responseText.setTextSize(18);

        layout.addView(title);
        layout.addView(input);
        layout.addView(send);
        layout.addView(responseText);

        setContentView(layout);

        send.setOnClickListener(
                v -> sendToBackend()
        );
    }


    // -----------------------------------------
    // SEND COMMAND TO VOLBY CORE
    // -----------------------------------------

    private void sendToBackend() {

        String message =
                input.getText()
                        .toString()
                        .trim();

        if (message.isEmpty()) {

            responseText.setText(
                    "Tell me what you want to do."
            );

            return;
        }

        responseText.setText(
                "Thinking..."
        );

        new Thread(() -> {

            try {

                String encoded =
                        URLEncoder.encode(
                                message,
                                "UTF-8"
                        );

                URL url =
                        new URL(
                                API_URL
                                        + "?message="
                                        + encoded
                        );

                HttpURLConnection connection =
                        (HttpURLConnection)
                                url.openConnection();

                connection.setRequestMethod(
                        "POST"
                );

                connection.setConnectTimeout(
                        10000
                );

                connection.setReadTimeout(
                        15000
                );

                int status =
                        connection.getResponseCode();

                BufferedReader reader;

                if (status >= 200 && status < 300) {

                    reader =
                            new BufferedReader(
                                    new InputStreamReader(
                                            connection
                                                    .getInputStream()
                                    )
                            );

                } else {

                    reader =
                            new BufferedReader(
                                    new InputStreamReader(
                                            connection
                                                    .getErrorStream()
                                    )
                            );
                }

                StringBuilder result =
                        new StringBuilder();

                String line;

                while (
                        (line =
                                reader.readLine())
                                != null
                ) {

                    result.append(line);
                }

                reader.close();
                connection.disconnect();

                if (status < 200 || status >= 300) {

                    final String error =
                            "Server error "
                                    + status
                                    + ":\n"
                                    + result;

                    runOnUiThread(() ->
                            responseText.setText(
                                    error
                            )
                    );

                    return;
                }

                JSONObject json =
                        new JSONObject(
                                result.toString()
                        );

                String response =
                        json.optString(
                                "response",
                                "No response."
                        );

                JSONObject action =
                        json.optJSONObject(
                                "action"
                        );

                runOnUiThread(() -> {

                    responseText.setText(
                            response
                    );

                    if (action != null) {

                        handleAction(
                                action
                        );
                    }
                });

            } catch (Exception e) {

                runOnUiThread(() ->
                        responseText.setText(
                                "Connection error:\n"
                                        + e.getMessage()
                        )
                );
            }

        }).start();
    }


    // -----------------------------------------
    // EXECUTE VOLBY ACTION
    // -----------------------------------------

    private void handleAction(
            JSONObject action
    ) {

        try {

            String actionType =
                    action.optString(
                            "action",
                            ""
                    );

            // -----------------------------
            // OPEN APP
            // -----------------------------

            if (
                    actionType.equals(
                            "open_app"
                    )
            ) {

                String appName =
                        action.optString(
                                "app",
                                ""
                        );

                if (appName.isEmpty()) {

                    responseText.setText(
                            "AI didn't specify an app."
                    );

                    return;
                }

                String packageName =
                        AppRegistry
                                .getPackageName(
                                        appName
                                );

                if (packageName == null) {

                    responseText.setText(
                            "I don't know how to open "
                                    + appName
                                    + " yet."
                    );

                    return;
                }

                String result =
                        AppLauncher.openApp(
                                this,
                                appName
                        );

                responseText.setText(
                        result
                );

                return;
            }


            // -----------------------------
            // OPEN WEBSITE
            // -----------------------------

            if (
                    actionType.equals(
                            "open_website"
                    )
            ) {

                String url =
                        action.optString(
                                "url",
                                ""
                        );

                if (url.isEmpty()) {

                    responseText.setText(
                            "AI didn't specify a website."
                    );

                    return;
                }

                String result =
                        AppLauncher.openWebsite(
                                this,
                                url
                        );

                responseText.setText(
                        result
                );

                return;
            }


            // -----------------------------
            // WEB SEARCH
            // -----------------------------

            if (
                    actionType.equals(
                            "web_search"
                    )
            ) {

                String query =
                        action.optString(
                                "query",
                                ""
                        );

                if (query.isEmpty()) {

                    responseText.setText(
                            "AI didn't specify what to search."
                    );

                    return;
                }

                String result =
                        AppLauncher.webSearch(
                                this,
                                query
                        );

                responseText.setText(
                        result
                );

                return;
            }


            // -----------------------------
            // UNKNOWN ACTION
            // -----------------------------

            if (!actionType.isEmpty()) {

                responseText.setText(
                        "Unknown action: "
                                + actionType
                );
            }

        } catch (Exception e) {

            responseText.setText(
                    "Action error:\n"
                            + e.getMessage()
            );
        }
    }
}