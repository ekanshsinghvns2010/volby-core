package com.volby.core.tools;

import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;

public class AppLauncher {

    public static String openApp(Context context, String packageName) {
        try {
            PackageManager packageManager = context.getPackageManager();

            Intent intent = packageManager.getLaunchIntentForPackage(packageName);

            if (intent == null) {
                return "App is not installed.";
            }

            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            context.startActivity(intent);

            return "App opened successfully.";

        } catch (Exception e) {
            return "Could not open app: " + e.getMessage();
        }
    }
}