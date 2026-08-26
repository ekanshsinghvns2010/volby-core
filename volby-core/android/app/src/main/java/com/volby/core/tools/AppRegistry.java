package com.volby.core.tools;

import java.util.HashMap;
import java.util.Map;

public class AppRegistry {

    private static final Map<String, String> APPS = new HashMap<>();

    static {
        APPS.put("youtube", "com.google.android.youtube");
APPS.put("chrome", "com.android.chrome");
APPS.put("whatsapp", "com.whatsapp");
APPS.put("instagram", "com.instagram.android");
APPS.put("facebook", "com.facebook.katana");
APPS.put("messenger", "com.facebook.orca");
APPS.put("linkedin", "com.linkedin.android");
APPS.put("play store", "com.android.vending");
APPS.put("google", "com.google.android.googlequicksearchbox");
APPS.put("gmail", "com.google.android.gm");
APPS.put("google maps", "com.google.android.apps.maps");
APPS.put("google photos", "com.google.android.apps.photos");
APPS.put("google drive", "com.google.android.apps.docs");
APPS.put("google meet", "com.google.android.apps.tachyon");
APPS.put("google calendar", "com.google.android.calendar");
APPS.put("google translate", "com.google.android.apps.translate");
APPS.put("youtube music", "com.google.android.apps.youtube.music");
APPS.put("spotify", "com.spotify.music");
APPS.put("telegram", "org.telegram.messenger");
APPS.put("snapchat", "com.snapchat.android");
APPS.put("reddit", "com.reddit.frontpage");
APPS.put("discord", "com.discord");
APPS.put("x", "com.twitter.android");
APPS.put("pinterest", "com.pinterest");
APPS.put("netflix", "com.netflix.mediaclient");
APPS.put("amazon", "in.amazon.mShop.android.shopping");
APPS.put("flipkart", "com.flipkart.android");
APPS.put("phonepe", "com.phonepe.app");
APPS.put("paytm", "net.one97.paytm");
APPS.put("zomato", "com.application.zomato");
APPS.put("swiggy", "in.swiggy.android");
    }

    public static String getPackageName(String appName) {
        if (appName == null) {
            return null;
        }

        return APPS.get(appName.trim().toLowerCase());
    }
}