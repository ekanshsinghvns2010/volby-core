package com.volby.core.tools;

import android.content.Context;
import android.content.Intent;
import android.content.pm.ApplicationInfo;
import android.content.pm.PackageManager;
import android.net.Uri;

import java.util.List;

public class AppLauncher {

    public static String openApp(
            Context context,
            String appName
    ) {
        try {

            PackageManager pm =
                    context.getPackageManager();

            List<ApplicationInfo> apps =
                    pm.getInstalledApplications(
                            PackageManager.GET_META_DATA
                    );

            for (ApplicationInfo app : apps) {

                String label =
                        pm.getApplicationLabel(app)
                                .toString();

                if (
                        label.equalsIgnoreCase(
                                appName.trim()
                        )
                ) {

                    Intent launchIntent =
                            pm.getLaunchIntentForPackage(
                                    app.packageName
                            );

                    if (launchIntent == null) {
                        return appName
                                + " cannot be launched.";
                    }

                    launchIntent.addFlags(
                            Intent.FLAG_ACTIVITY_NEW_TASK
                    );

                    context.startActivity(
                            launchIntent
                    );

                    return "Opening "
                            + label
                            + "...";
                }
            }

            return appName
                    + " is not installed.";

        } catch (Exception e) {

            return "Could not open "
                    + appName
                    + ": "
                    + e.getMessage();
        }
    }


    // -----------------------------------------
    // OPEN WEBSITE
    // -----------------------------------------

    public static String openWebsite(
            Context context,
            String url
    ) {

        try {

            if (
                    !url.startsWith("http://")
                    && !url.startsWith("https://")
            ) {

                url = "https://" + url;
            }

            Intent intent =
                    new Intent(
                            Intent.ACTION_VIEW,
                            Uri.parse(url)
                    );

            intent.addFlags(
                    Intent.FLAG_ACTIVITY_NEW_TASK
            );

            context.startActivity(intent);

            return "Opening website...";

        } catch (Exception e) {

            return "Could not open website: "
                    + e.getMessage();
        }
    }


    // -----------------------------------------
    // WEB SEARCH
    // -----------------------------------------

    public static String webSearch(
            Context context,
            String query
    ) {

        try {

            String encodedQuery =
                    Uri.encode(query);

            String url =
                    "https://www.google.com/search?q="
                            + encodedQuery;

            Intent intent =
                    new Intent(
                            Intent.ACTION_VIEW,
                            Uri.parse(url)
                    );

            intent.addFlags(
                    Intent.FLAG_ACTIVITY_NEW_TASK
            );

            context.startActivity(intent);

            return "Searching for "
                    + query
                    + "...";

        } catch (Exception e) {

            return "Could not perform search: "
                    + e.getMessage();
        }
    }
}