package com.volby.core.accessibility;

import android.accessibilityservice.AccessibilityService;
import android.view.accessibility.AccessibilityEvent;
import android.view.accessibility.AccessibilityNodeInfo;

public class VolbyAccessibilityService extends AccessibilityService {

    private static VolbyAccessibilityService instance;

    @Override
    protected void onServiceConnected() {
        super.onServiceConnected();
        instance = this;
    }

    @Override
    public void onAccessibilityEvent(AccessibilityEvent event) {
        // Volby can inspect the current screen through the root node.
    }

    @Override
    public void onInterrupt() {
    }

    @Override
    public void onDestroy() {
        instance = null;
        super.onDestroy();
    }

    public static VolbyAccessibilityService getInstance() {
        return instance;
    }

    public AccessibilityNodeInfo getCurrentRoot() {
        return getRootInActiveWindow();
    }
}