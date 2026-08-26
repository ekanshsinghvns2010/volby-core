package com.volby.core;

import android.app.Activity;
import android.os.Bundle;
import android.widget.TextView;

public class MainActivity extends Activity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        TextView statusText = new TextView(this);
        statusText.setText("Volby Core\nAndroid component online.");
        setContentView(statusText);
    }
}