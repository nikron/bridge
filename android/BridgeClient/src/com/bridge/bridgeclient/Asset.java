package com.bridge.bridgeclient;

import java.util.Iterator;
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
    private String[][] status;
    private String[] actionURLs;

    public Asset(String assetJSON) throws JSONException
    {
        JSONObject obj = new JSONObject(assetJSON);

        name = obj.getString("name");
        realID = obj.getString("real id");
        uuid = obj.getString("uuid");
        JSONObject statusObj = obj.getJSONObject("state");
        status = new String[statusObj.length()][2];

        int j = 0;
        Iterator<String> categories = statusObj.keys();
        for (String category; categories.hasNext();)
        {
            category = categories.next();
            status[j] = new String[2];
            status[j][0] = category;
            status[j][1] = statusObj.getString(category);
            j++;
        }

        JSONArray actionJSONURLs = obj.getJSONArray("action_urls");
        actionURLs = new String[actionJSONURLs.length()];
        for (j = 0; j < actionJSONURLs.length(); j++)
            actionURLs[j] = actionJSONURLs.getString(j);

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
        return status.length;
    }

    public String getCategory(int i)
    {
        return status[i][0];
    }

    public String getStatus(int i)
    {
        return status[i][1];
    }

    public String toString()
    {
        return getName();
    }
}
