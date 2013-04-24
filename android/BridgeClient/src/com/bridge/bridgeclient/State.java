package com.bridge.bridgeclient;

import org.json.JSONObject;
import org.json.JSONArray;
import org.json.JSONException;

public class State
{
    public static final String BINARY_TYPE = "binary";

    private boolean controllable;
    private boolean unknown;
    private boolean currentBool;
    private int currentInt;
    private String type;


    public State(JSONObject stateJSON) throws JSONException
    {
        controllable = stateJSON.getBoolean("controllable");
        unknown = stateJSON.getBoolean("unknown");
        type = stateJSON.getString("type");

        if (! isUnknown() && isBinary())
        {
            currentBool = stateJSON.getBoolean("current");
        }
    }

    public boolean isUnknown()
    {
       return unknown;
    }

    public boolean isControllabel()
    {
        return controllable;
    }

    public boolean isBinary()
    {
        return type.equals(BINARY_TYPE);
    }

    public boolean isSwitchable()
    {
        return ! unknown && controllable && this.isBinary();
    }
}
