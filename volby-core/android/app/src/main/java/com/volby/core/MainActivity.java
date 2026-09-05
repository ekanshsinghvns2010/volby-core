package com.volby.core;

import android.Manifest;
import android.app.Activity;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.Bundle;
import android.speech.RecognitionListener;
import android.speech.RecognizerIntent;
import android.speech.SpeechRecognizer;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.TextView;

import com.volby.core.tools.ActionExecutor;

import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLEncoder;
import java.util.ArrayList;
import java.util.Locale;

public class MainActivity extends Activity {

    private static final String API_URL =
            "https://volby-core-api.onrender.com/chat";

    private static final int MIC_PERMISSION = 1001;

    private EditText input;
    private TextView responseText;
    private Button sendButton;
    private Button voiceButton;

    private SpeechRecognizer speechRecognizer;

    private boolean listening = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        createUI();
        setupSpeechRecognizer();
        requestMicrophonePermission();
    }

    // ==================================================
    // UI
    // ==================================================

    private void createUI() {

        LinearLayout layout =
                new LinearLayout(this);

        layout.setOrientation(
                LinearLayout.VERTICAL
        );

        layout.setPadding(
                32, 32, 32, 32
        );

        TextView title =
                new TextView(this);

        title.setText("Volby Core");
        title.setTextSize(28);

        input =
                new EditText(this);

        input.setHint(
                "Type or speak a command..."
        );

        input.setTextSize(18);

        sendButton =
                new Button(this);

        sendButton.setText("Send");

        voiceButton =
                new Button(this);

        voiceButton.setText("🎤 Speak");

        responseText =
                new TextView(this);

        responseText.setText(
                "Volby is ready."
        );

        responseText.setTextSize(18);

        layout.addView(title);
        layout.addView(input);
        layout.addView(sendButton);
        layout.addView(voiceButton);
        layout.addView(responseText);

        setContentView(layout);

        // Manual text command
        sendButton.setOnClickListener(
                v -> sendToBackend(
                        input.getText()
                                .toString()
                                .trim()
                )
        );

        // Voice command
        voiceButton.setOnClickListener(
                v -> toggleVoice()
        );
    }

    // ==================================================
    // MICROPHONE PERMISSION
    // ==================================================

    private void requestMicrophonePermission() {

        if (
                checkSelfPermission(
                        Manifest.permission.RECORD_AUDIO
                ) != PackageManager.PERMISSION_GRANTED
        ) {

            requestPermissions(
                    new String[]{
                            Manifest.permission.RECORD_AUDIO
                    },
                    MIC_PERMISSION
            );
        }
    }

    // ==================================================
    // SPEECH RECOGNIZER
    // ==================================================

    private void setupSpeechRecognizer() {

        if (
                !SpeechRecognizer
                        .isRecognitionAvailable(this)
        ) {

            voiceButton.setEnabled(false);

            responseText.setText(
                    "Speech recognition is not available."
            );

            return;
        }

        speechRecognizer =
                SpeechRecognizer
                        .createSpeechRecognizer(this);

        speechRecognizer.setRecognitionListener(
                new RecognitionListener() {

                    @Override
                    public void onReadyForSpeech(
                            Bundle params
                    ) {

                        listening = true;

                        voiceButton.setText(
                                "🔴 Listening..."
                        );

                        responseText.setText(
                                "Listening..."
                        );
                    }

                    @Override
                    public void onBeginningOfSpeech() {
                    }

                    @Override
                    public void onRmsChanged(
                            float rmsdB
                    ) {
                    }

                    @Override
                    public void onBufferReceived(
                            byte[] buffer
                    ) {
                    }

                    @Override
                    public void onEndOfSpeech() {

                        listening = false;

                        voiceButton.setText(
                                "🎤 Speak"
                        );

                        responseText.setText(
                                "Processing..."
                        );
                    }

                    @Override
                    public void onError(
                            int error
                    ) {

                        listening = false;

                        voiceButton.setText(
                                "🎤 Speak"
                        );

                        responseText.setText(
                                speechError(error)
                        );
                    }

                    // ==================================================
                    // VOICE RESULT
                    // ==================================================

                    @Override
                    public void onResults(
                            Bundle results
                    ) {

                        listening = false;

                        voiceButton.setText(
                                "🎤 Speak"
                        );

                        ArrayList<String> matches =
                                results.getStringArrayList(
                                        SpeechRecognizer
                                                .RESULTS_RECOGNITION
                                );

                        if (
                                matches != null
                                &&
                                !matches.isEmpty()
                        ) {

                            String command =
                                    matches.get(0).trim();

                            // Put recognized speech into text box
                            input.setText(command);

                            responseText.setText(
                                    "You said:\n"
                                            + command
                                            + "\n\n"
                                            + "Volby is thinking..."
                            );

                            // ==================================================
                            // IMPORTANT:
                            // AUTOMATICALLY SEND VOICE COMMAND
                            // ==================================================

                            sendToBackend(command);

                        } else {

                            responseText.setText(
                                    "I couldn't understand that."
                            );
                        }
                    }

                    @Override
                    public void onPartialResults(
                            Bundle partialResults
                    ) {
                    }

                    @Override
                    public void onEvent(
                            int eventType,
                            Bundle params
                    ) {
                    }
                }
        );
    }

    // ==================================================
    // VOICE BUTTON
    // ==================================================

    private void toggleVoice() {

        if (
                checkSelfPermission(
                        Manifest.permission.RECORD_AUDIO
                ) != PackageManager.PERMISSION_GRANTED
        ) {

            requestMicrophonePermission();

            return;
        }

        if (speechRecognizer == null) {

            setupSpeechRecognizer();

            return;
        }

        if (listening) {

            speechRecognizer.stopListening();

            listening = false;

            voiceButton.setText(
                    "🎤 Speak"
            );

        } else {

            startListening();
        }
    }

    // ==================================================
    // START LISTENING
    // ==================================================

    private void startListening() {

        Intent intent =
                new Intent(
                        RecognizerIntent
                                .ACTION_RECOGNIZE_SPEECH
                );

        intent.putExtra(
                RecognizerIntent.EXTRA_LANGUAGE_MODEL,
                RecognizerIntent
                        .LANGUAGE_MODEL_FREE_FORM
        );

        intent.putExtra(
                RecognizerIntent.EXTRA_LANGUAGE,
                Locale.getDefault()
        );

        intent.putExtra(
                RecognizerIntent.EXTRA_MAX_RESULTS,
                3
        );

        intent.putExtra(
                RecognizerIntent.EXTRA_PARTIAL_RESULTS,
                true
        );

        try {

            speechRecognizer.startListening(
                    intent
            );

        } catch (Exception e) {

            responseText.setText(
                    "Could not start microphone:\n"
                            + e.getMessage()
            );
        }
    }

    // ==================================================
    // SPEECH ERRORS
    // ==================================================

    private String speechError(
            int error
    ) {

        switch (error) {

            case SpeechRecognizer.ERROR_AUDIO:
                return "Microphone audio error.";

            case SpeechRecognizer.ERROR_INSUFFICIENT_PERMISSIONS:
                return "Microphone permission denied.";

            case SpeechRecognizer.ERROR_NETWORK:
                return "Speech network error.";

            case SpeechRecognizer.ERROR_NETWORK_TIMEOUT:
                return "Speech network timeout.";

            case SpeechRecognizer.ERROR_NO_MATCH:
                return "I couldn't understand you.";

            case SpeechRecognizer.ERROR_RECOGNIZER_BUSY:
                return "Speech recognizer is busy.";

            case SpeechRecognizer.ERROR_SPEECH_TIMEOUT:
                return "I didn't hear anything.";

            default:
                return "Voice error: " + error;
        }
    }

    // ==================================================
    // SEND TO VOLBY BACKEND
    // ==================================================

    private void sendToBackend(
            String message
    ) {

        if (
                message == null ||
                message.trim().isEmpty()
        ) {

            responseText.setText(
                    "Enter or speak a command first."
            );

            return;
        }

        sendButton.setEnabled(false);
        voiceButton.setEnabled(false);

        responseText.setText(
                "Volby is thinking..."
        );

        new Thread(() -> {

            HttpURLConnection connection = null;

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

                connection =
                        (HttpURLConnection)
                                url.openConnection();

                connection.setRequestMethod(
                        "POST"
                );

                connection.setConnectTimeout(
                        15000
                );

                connection.setReadTimeout(
                        30000
                );

                int code =
                        connection.getResponseCode();

                BufferedReader reader =
                        new BufferedReader(
                                new InputStreamReader(
                                        code >= 200 &&
                                        code < 300
                                        ?
                                        connection
                                                .getInputStream()
                                        :
                                        connection
                                                .getErrorStream()
                                )
                        );

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

                if (
                        code < 200 ||
                        code >= 300
                ) {

                    throw new Exception(
                            "HTTP "
                                    + code
                                    + ": "
                                    + result
                    );
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

                    sendButton.setEnabled(true);
                    voiceButton.setEnabled(true);

                    responseText.setText(
                            response
                    );

                    // ==================================================
                    // EXECUTE ACTION AUTOMATICALLY
                    // ==================================================

                    if (action != null) {

                        executeAction(action);
                    }
                });

            } catch (Exception e) {

                runOnUiThread(() -> {

                    sendButton.setEnabled(true);
                    voiceButton.setEnabled(true);

                    responseText.setText(
                            "Connection error:\n"
                                    + e.getMessage()
                    );
                });

            } finally {

                if (connection != null) {

                    connection.disconnect();
                }
            }

        }).start();
    }

    // ==================================================
    // ACTION EXECUTOR
    // ==================================================

    private void executeAction(
            JSONObject action
    ) {

        try {

            String actionType =
                    action.optString(
                            "action",
                            ""
                    );

            String value = null;

            if (action.has("app")) {

                value =
                        action.optString(
                                "app"
                        );

            } else if (action.has("url")) {

                value =
                        action.optString(
                                "url"
                        );

            } else if (action.has("query")) {

                value =
                        action.optString(
                                "query"
                        );

            } else if (action.has("text")) {

                value =
                        action.optString(
                                "text"
                        );
            }

            String finalValue = value;

            new Thread(() -> {

                String result =
                        ActionExecutor.execute(
                                MainActivity.this,
                                actionType,
                                finalValue
                        );

                runOnUiThread(() ->
                        responseText.setText(
                                result
                        )
                );

            }).start();

        } catch (Exception e) {

            responseText.setText(
                    "Action error:\n"
                            + e.getMessage()
            );
        }
    }

    // ==================================================
    // CLEANUP
    // ==================================================

    @Override
    protected void onDestroy() {

        if (speechRecognizer != null) {

            speechRecognizer.destroy();

            speechRecognizer = null;
        }

        super.onDestroy();
    }
}