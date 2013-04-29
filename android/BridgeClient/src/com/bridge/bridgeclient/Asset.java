package com.bridge.bridgeclient;

import java.util.Iterator;
import java.util.HashMap;
import java.net.URI;

import org.json.JSONObject;
import org.json.JSONArray;
import org.json.JSONException;

public class Asset
{
    private String name;
    private String realID;
    private String url;
    private String uuid;
    private HashMap<String, State> status;
    private String[] actionURLs;

    public Asset(String assetJSON) throws JSONException
    {
        JSONObject obj = new JSONObject(assetJSON);

        name = obj.getString("name");
        realID = obj.getString("real id");
        url = obj.getString("url");
        uuid = obj.getString("uuid");
        uuid = obj.getString("uuid");
        JSONObject statusObj = obj.getJSONObject("state");
        status = new HashMap<String, State>();

        Iterator<String> categories = statusObj.keys();
        for (String category; categories.hasNext();)
        {
            category = categories.next();
            status.put(category, new State(category, statusObj.getJSONObject(category)));
        }

        JSONArray actionJSONURLs = obj.getJSONArray("action_urls");
        actionURLs = new String[actionJSONURLs.length()];
        for (int i = 0; i < actionJSONURLs.length(); i++)
            actionURLs[i] = actionJSONURLs.getString(i);

    }

    public boolean isMainEnabled()
    {
        State main = status.get("main");
        if (main == null)
            return false;
        else
            return main.isEnabled();
    }

    public boolean getCurrentMainState()
    {
        State main = status.get("main");
        if (main == null)
            return false;
        else
            return main.getCurrent();
    }

    public int getMainType()
    {
        State main = status.get("main");
        if (main == null)
            return State.UNKNOWN_TYPE;
        else
            return main.getType();
    }
    

    public String getName()
    {
        return name;
    }

    public String getRealID()
    {
        return realID;
    }

    public String getURL()
    {
        return url;
    }

    public String getUUID()
    {
        return uuid;
    }

    public String setCurrentMainState(boolean state)
    {
        State main = status.get("main");
        String patch = main.setState(state);
        return patch;
    }

    public String setCurrentMainState(int state)
    {
        State main = status.get("main");
        String patch = main.setState(state);
        return patch;
    }

    public int numberOfCategories()
    {
        return status.size();
    }

    public String toString()
    {
        return getName();
    }

}
