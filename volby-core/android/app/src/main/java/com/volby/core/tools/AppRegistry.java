package com.volby.core.tools;

import java.util.HashMap;
import java.util.Map;

public class AppRegistry {

    private static final Map<String, String> APPS = new HashMap<>();

    static {
        APPS.put("youtube", "com.google.android.youtube");
        APPS.put("chrome", "com.android.chrome");
        APPS.put("whatsapp", "com.whatsapp");
    }

    public static String getPackageName(String appName) {
        if (appName == null) {
            return null;
        }

        return APPS.get(appName.trim().toLowerCase());
    }
}