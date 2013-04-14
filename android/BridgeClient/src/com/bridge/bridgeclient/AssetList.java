package com.bridge.bridgeclient;

import java.util.ArrayList;
import java.net.URI;

import org.json.JSONArray;
import org.json.JSONObject;
import org.json.JSONException;
import java.io.IOException;
import org.apache.http.client.ClientProtocolException;

class AssetList
{
    URI url;
    ArrayList<Asset> assets;

    public AssetList()
    {
        this.url = null;
        assets = new ArrayList<Asset>();
    }

    public void refresh() throws JSONException, IOException, ClientProtocolException
    {
        assets.clear();

        if (url != null) {
            String assetURLs = Utility.getURL(url);
            JSONObject obj = new JSONObject(assetURLs);
            JSONArray urlArray = obj.getJSONArray("assets_urls");

            for (int i = 0; i < urlArray.length(); i++)
            {
                assets.add(new Asset(urlArray.getString(i)));
            }
        }
    }

    public int length()
    {
        return assets.size();
    }

    public Asset get(int i)
    {
        return assets.get(i);
    }

    public void setURL(URI url)
    {
        this.url = url;
    }
}
