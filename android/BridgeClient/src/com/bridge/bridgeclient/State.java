package com.bridge.bridgeclient;

import org.json.JSONObject;
import org.json.JSONArray;
import org.json.JSONException;

public class State
{
    public static final int BINARY_TYPE = 0;
    public static final int RANGE_TYPE = 1;
    public static final int UNKNOWN_TYPE = 2;

    private String category;
    private boolean controllable;
    private boolean unknown;
    private boolean currentBool;
    private int currentInt;
    private int type;


    public State(String category, JSONObject stateJSON) throws JSONException
    {
        this.category = category;
        controllable = stateJSON.getBoolean("controllable");
        unknown = stateJSON.getBoolean("unknown");
        String strType = stateJSON.getString("type");

        if (strType.equals("binary"))
            type = BINARY_TYPE;
        else if (strType.equals("range"))
            type = RANGE_TYPE;
        else
            type = UNKNOWN_TYPE;

        if (! unknown && type == BINARY_TYPE)
        {
            currentBool = stateJSON.getBoolean("current");
        }
        else if ( ! unknown && type == RANGE_TYPE)
        {
            currentInt = stateJSON.getInt("current");
        }
    }

    public boolean getCurrent()
    {
        return currentBool;
    }

    public int getType()
    {
        return type;
    }

    public boolean isUnknown()
    {
        return unknown;
    }

    public boolean isControllabel()
    {
        return controllable;
    }

    public boolean isEnabled()
    {
        return ! unknown && controllable;
    }

    public String setState(boolean state)
    {
        currentBool = state;

        String patch = "[{ \"op\": \"replace\", \"path\": \"/state/" + category + "/current\", \"value\": " + Boolean.toString(currentBool) + " }]";
        return patch;
    }

    public String setState(int state)
    {
        currentInt = state;

        String patch = "[{ \"op\": \"replace\", \"path\": \"/state/" + category + "/current\", \"value\": " + Integer.toString(currentInt) + " }]";
        return patch;
    }
}
