package com.volby.core.tools;

import android.accessibilityservice.AccessibilityService;
import android.content.Context;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.view.accessibility.AccessibilityNodeInfo;

import com.volby.core.accessibility.VolbyAccessibilityService;

import java.util.List;

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
                return goBack();


            case "go_home":
                return goHome();


            case "press_enter":
                return pressEnter();


            case "type_text":
                if (value == null) {
                    value = "";
                }

                return typeText(value);


            case "tap":
                return tapElement(value);


            case "scroll":
                return scrollScreen(value);


            default:
                return "Unknown action: " + action;
        }
    }


    // ---------------------------------------------------------
    // BACK
    // ---------------------------------------------------------

    private static String goBack() {

        VolbyAccessibilityService service =
                VolbyAccessibilityService.getInstance();

        if (service == null) {
            return "Accessibility Service is not enabled.";
        }

        boolean result =
                service.performGlobalAction(
                        AccessibilityService.GLOBAL_ACTION_BACK
                );

        return result
                ? "Going back."
                : "Could not go back.";
    }


    // ---------------------------------------------------------
    // HOME
    // ---------------------------------------------------------

    private static String goHome() {

        VolbyAccessibilityService service =
                VolbyAccessibilityService.getInstance();

        if (service == null) {
            return "Accessibility Service is not enabled.";
        }

        boolean result =
                service.performGlobalAction(
                        AccessibilityService.GLOBAL_ACTION_HOME
                );

        return result
                ? "Going home."
                : "Could not go home.";
    }


    // ---------------------------------------------------------
    // TYPE TEXT
    // ---------------------------------------------------------

    private static String typeText(String text) {

        VolbyAccessibilityService service =
                VolbyAccessibilityService.getInstance();

        if (service == null) {
            return "Accessibility Service is not enabled.";
        }

        AccessibilityNodeInfo root =
                service.getCurrentRoot();

        if (root == null) {
            return "Could not read the current screen.";
        }

        AccessibilityNodeInfo target =
                findEditableNode(root);

        if (target == null) {
            return "I could not find a text field.";
        }

        try {

            Bundle arguments = new Bundle();

            arguments.putCharSequence(
                    AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE,
                    text
            );

            boolean result =
                    target.performAction(
                            AccessibilityNodeInfo.ACTION_SET_TEXT,
                            arguments
                    );

            if (result) {
                return "Typed: " + text;
            }

            return "I found the text field, but could not type.";

        } finally {

            target.recycle();
        }
    }


    // ---------------------------------------------------------
    // FIND EDITABLE FIELD
    // ---------------------------------------------------------

    private static AccessibilityNodeInfo findEditableNode(
            AccessibilityNodeInfo node
    ) {

        if (node == null) {
            return null;
        }

        if (node.isEditable()) {
            return node;
        }

        String className =
                node.getClassName() == null
                        ? ""
                        : node.getClassName().toString();

        if (className.contains("EditText")) {
            return node;
        }

        int childCount =
                node.getChildCount();

        for (int i = 0; i < childCount; i++) {

            AccessibilityNodeInfo child =
                    node.getChild(i);

            AccessibilityNodeInfo result =
                    findEditableNode(child);

            if (result != null) {
                return result;
            }

            if (child != null) {
                child.recycle();
            }
        }

        return null;
    }


    // ---------------------------------------------------------
    // PRESS ENTER / SEARCH
    // ---------------------------------------------------------

    private static String pressEnter() {

        VolbyAccessibilityService service =
                VolbyAccessibilityService.getInstance();

        if (service == null) {
            return "Accessibility Service is not enabled.";
        }

        AccessibilityNodeInfo root =
                service.getCurrentRoot();

        if (root == null) {
            return "Could not read the current screen.";
        }

        AccessibilityNodeInfo editable =
                findEditableNode(root);

        if (editable != null) {

            try {

                /*
                 * Many Android search fields expose an IME action.
                 * Clicking the focused/search field can trigger
                 * the keyboard action in supported applications.
                 */

                if (editable.isFocused()) {

                    boolean clicked =
                            editable.performAction(
                                    AccessibilityNodeInfo.ACTION_CLICK
                            );

                    if (clicked) {
                        return "Pressed enter.";
                    }
                }

            } finally {
                editable.recycle();
            }
        }

        /*
         * If no editable field worked, search for a visible
         * button such as Search, Go, Done, or Enter.
         */

        AccessibilityNodeInfo button =
                findActionButton(root);

        if (button != null) {

            try {

                boolean result =
                        button.performAction(
                                AccessibilityNodeInfo.ACTION_CLICK
                        );

                if (result) {
                    return "Pressed enter.";
                }

            } finally {
                button.recycle();
            }
        }

        return "Could not press enter on this screen.";
    }


    // ---------------------------------------------------------
    // FIND SEARCH / GO / DONE BUTTON
    // ---------------------------------------------------------

    private static AccessibilityNodeInfo findActionButton(
            AccessibilityNodeInfo node
    ) {

        if (node == null) {
            return null;
        }

        CharSequence text =
                node.getText();

        CharSequence description =
                node.getContentDescription();

        String combined = "";

        if (text != null) {
            combined += text.toString().toLowerCase() + " ";
        }

        if (description != null) {
            combined += description.toString().toLowerCase();
        }

        if (node.isClickable()) {

            if (combined.contains("search")
                    || combined.contains("go")
                    || combined.contains("done")
                    || combined.contains("enter")
                    || combined.contains("submit")) {

                return node;
            }
        }

        int childCount =
                node.getChildCount();

        for (int i = 0; i < childCount; i++) {

            AccessibilityNodeInfo child =
                    node.getChild(i);

            AccessibilityNodeInfo result =
                    findActionButton(child);

            if (result != null) {
                return result;
            }

            if (child != null) {
                child.recycle();
            }
        }

        return null;
    }


    // ---------------------------------------------------------
    // TAP
    // ---------------------------------------------------------

    private static String tapElement(String targetText) {

        VolbyAccessibilityService service =
                VolbyAccessibilityService.getInstance();

        if (service == null) {
            return "Accessibility Service is not enabled.";
        }

        if (targetText == null
                || targetText.trim().isEmpty()) {

            return "No element specified to tap.";
        }

        AccessibilityNodeInfo root =
                service.getCurrentRoot();

        if (root == null) {
            return "Could not read the current screen.";
        }

        AccessibilityNodeInfo target =
                findClickableElement(
                        root,
                        targetText
                );

        if (target == null) {
            return "Could not find: " + targetText;
        }

        try {

            boolean result =
                    target.performAction(
                            AccessibilityNodeInfo.ACTION_CLICK
                    );

            return result
                    ? "Tapped " + targetText + "."
                    : "Found " + targetText
                        + " but could not tap it.";

        } finally {

            target.recycle();
        }
    }


    // ---------------------------------------------------------
    // FIND CLICKABLE ELEMENT
    // ---------------------------------------------------------

    private static AccessibilityNodeInfo findClickableElement(
            AccessibilityNodeInfo node,
            String targetText
    ) {

        if (node == null) {
            return null;
        }

        String target =
                targetText
                        .trim()
                        .toLowerCase();

        CharSequence text =
                node.getText();

        CharSequence description =
                node.getContentDescription();

        String nodeText = "";

        if (text != null) {
            nodeText += text.toString().toLowerCase();
        }

        if (description != null) {
            nodeText += " "
                    + description.toString().toLowerCase();
        }

        if (node.isClickable()
                && nodeText.contains(target)) {

            return node;
        }

        int childCount =
                node.getChildCount();

        for (int i = 0; i < childCount; i++) {

            AccessibilityNodeInfo child =
                    node.getChild(i);

            AccessibilityNodeInfo result =
                    findClickableElement(
                            child,
                            targetText
                    );

            if (result != null) {
                return result;
            }

            if (child != null) {
                child.recycle();
            }
        }

        return null;
    }


    // ---------------------------------------------------------
    // SCROLL
    // ---------------------------------------------------------

    private static String scrollScreen(String direction) {

        VolbyAccessibilityService service =
                VolbyAccessibilityService.getInstance();

        if (service == null) {
            return "Accessibility Service is not enabled.";
        }

        AccessibilityNodeInfo root =
                service.getCurrentRoot();

        if (root == null) {
            return "Could not read the current screen.";
        }

        AccessibilityNodeInfo scrollable =
                findScrollableNode(root);

        if (scrollable == null) {
            return "Could not find a scrollable area.";
        }

        try {

            int action =
                    AccessibilityNodeInfo
                            .ACTION_SCROLL_FORWARD;

            if (direction != null
                    && direction
                    .toLowerCase()
                    .contains("up")) {

                action =
                        AccessibilityNodeInfo
                                .ACTION_SCROLL_BACKWARD;
            }

            boolean result =
                    scrollable.performAction(action);

            return result
                    ? "Scrolled " + direction + "."
                    : "Could not scroll.";

        } finally {

            scrollable.recycle();
        }
    }


    // ---------------------------------------------------------
    // FIND SCROLLABLE NODE
    // ---------------------------------------------------------

    private static AccessibilityNodeInfo findScrollableNode(
            AccessibilityNodeInfo node
    ) {

        if (node == null) {
            return null;
        }

        if (node.isScrollable()) {
            return node;
        }

        int childCount =
                node.getChildCount();

        for (int i = 0; i < childCount; i++) {

            AccessibilityNodeInfo child =
                    node.getChild(i);

            AccessibilityNodeInfo result =
                    findScrollableNode(child);

            if (result != null) {
                return result;
            }

            if (child != null) {
                child.recycle();
            }
        }

        return null;
    }


    // ---------------------------------------------------------
    // OPEN WEBSITE
    // ---------------------------------------------------------

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


    // ---------------------------------------------------------
    // WEB SEARCH
    // ---------------------------------------------------------

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