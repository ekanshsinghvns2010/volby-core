package com.volby.core.tools;

import android.content.Context;
import android.content.Intent;
import android.content.pm.ApplicationInfo;
import android.content.pm.PackageManager;

import java.util.List;

public class AppLauncher {

    public static String openApp(Context context, String appName) {
        try {
            PackageManager pm = context.getPackageManager();

            List<ApplicationInfo> apps =
                    pm.getInstalledApplications(PackageManager.GET_META_DATA);

            for (ApplicationInfo app : apps) {

                String label =
                        pm.getApplicationLabel(app).toString();

                if (label.equalsIgnoreCase(appName.trim())) {

                    Intent launchIntent =
                            pm.getLaunchIntentForPackage(app.packageName);

                    if (launchIntent == null) {
                        return appName + " cannot be launched.";
                    }

                    launchIntent.addFlags(
                            Intent.FLAG_ACTIVITY_NEW_TASK
                    );

                    context.startActivity(launchIntent);

                    return "Opening " + label + "...";
                }
            }

            return appName + " is not installed.";

        } catch (Exception e) {
            return "Could not open " + appName + ": "
                    + e.getMessage();
        }
    }
}