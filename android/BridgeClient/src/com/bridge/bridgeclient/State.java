package com.bridge.bridgeclient;

import org.json.JSONObject;
import org.json.JSONArray;
import org.json.JSONException;

public class State
{
    public static final int BINARY_TYPE = 0;
    public static final int RANGE_TYPE = 1;
    public static final int UNKNOWN_TYPE = 2;

    private boolean controllable;
    private boolean unknown;
    private boolean currentBool;
    private int currentInt;
    private int type;


    public State(JSONObject stateJSON) throws JSONException
    {
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
}
