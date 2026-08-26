package com.volby.core.tools;

import android.content.Context;
import android.content.Intent;
import android.net.Uri;

public class ActionExecutor {

    public static String execute(
            Context context,
            String action,
            String value
    ) {

        if (action == null) {
            return "No action received.";
        }

        switch (action) {

            case "open_app":

                if (value == null || value.trim().isEmpty()) {
                    return "No app specified.";
                }

                return AppLauncher.openApp(
                        context,
                        value
                );


            case "open_website":

                if (value == null || value.trim().isEmpty()) {
                    return "No website specified.";
                }

                return openWebsite(
                        context,
                        value
                );


            case "web_search":

                if (value == null || value.trim().isEmpty()) {
                    return "No search query specified.";
                }

                return searchWeb(
                        context,
                        value
                );


            case "go_back":

                return "Back action received.";


            case "go_home":

                return "Home action received.";


            case "press_enter":

                return "Enter action received.";


            case "type_text":

                return "Type action received: " + value;


            case "tap":

                return "Tap action received.";


            case "scroll":

                return "Scroll action received.";


            default:

                return "Unknown action: " + action;
        }
    }


    private static String openWebsite(
            Context context,
            String url
    ) {

        try {

            if (!url.startsWith("http://")
                    && !url.startsWith("https://")) {

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

            return "Opening " + url + "...";

        } catch (Exception e) {

            return "Could not open website: "
                    + e.getMessage();
        }
    }


    private static String searchWeb(
            Context context,
            String query
    ) {

        try {

            String encoded =
                    Uri.encode(query);

            String url =
                    "https://www.google.com/search?q="
                            + encoded;

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

            return "Could not search: "
                    + e.getMessage();
        }
    }
}