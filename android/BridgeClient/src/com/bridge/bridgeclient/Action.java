package com.bridge.bridgeclient;

import org.json.JSONObject;
import org.json.JSONArray;
import org.json.JSONException;

import java.io.IOException;
import org.apache.http.client.ClientProtocolException;
import java.net.URISyntaxException;

class Action
{
    private String name;
    private String url;
    private String[] arguments;

    public Action(String url) throws ClientProtocolException, IOException, JSONException, URISyntaxException
    {
        this.url = url;

        JSONObject obj = new JSONObject(Utility.getURL(url));
        name = obj.getString("name");

        JSONArray args = obj.getJSONArray("arguments");

        if (0 < args.length())
        {
            arguments = new String[args.length()];
            for (int i = 0; i < args.length(); i++)
            {
                arguments[i] = new String(args.getString(i));
            }
        }
        else
        {
            arguments = null;
        }
    }

    public String getName()
    {
        return name;
    }

    public void doAction() throws IOException
    {
        Utility.postURL(url);
    }

    public boolean hasArguments()
    {
        if (arguments == null) return true;
        else return false;
    }
}
