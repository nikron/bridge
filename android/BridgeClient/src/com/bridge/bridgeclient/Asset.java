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
        uuid = obj.getString("uuid");
        JSONObject statusObj = obj.getJSONObject("state");
        status = new HashMap<String, State>();

        Iterator<String> categories = statusObj.keys();
        for (String category; categories.hasNext();)
        {
            category = categories.next();
            status.put(category, new State(statusObj.getJSONObject(category)));
        }

        JSONArray actionJSONURLs = obj.getJSONArray("action_urls");
        actionURLs = new String[actionJSONURLs.length()];
        for (int i = 0; i < actionJSONURLs.length(); i++)
            actionURLs[i] = actionJSONURLs.getString(i);

    }

    public String getName()
    {
        return name;
    }

    public String getRealID()
    {
        return realID;
    }

    public String getUUID()
    {
        return uuid;
    }

    public int numberOfCategories()
    {
        return status.size();
    }

    public String toString()
    {
        return getName();
    }

    public boolean hasSwitchableMain()
    {
        State main = status.get("main");
        if (main != null && main.isSwitchable())
            return true;
        else
            return false;
    }
}
