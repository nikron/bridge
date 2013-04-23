package com.bridge.bridgeclient;

import android.os.Bundle;
import android.os.ResultReceiver;
import android.content.Intent;
import android.app.IntentService;

import android.content.SharedPreferences;
import android.preference.PreferenceManager;

import java.net.URI;

import org.json.JSONObject;
import org.json.JSONArray;
import org.json.JSONException;

import java.io.IOException;
import org.apache.http.client.ClientProtocolException;
import java.net.URISyntaxException;

public class BridgeClientService extends IntentService
{
    public static final String COMMAND_KEY = "command";
    public static final String RECEIVER_KEY = "receiver";
    public static final String RESULTS_KEY = "results";

    public static final int NONE_COMMAND = 0; //please never use this
    public static final int GET_ASSETS_COMMAND = 1;

    public static final int STATUS_ERROR = 0;
    public static final int STATUS_GET_ASSETS_FINISHED = 1;
    public static final int STATUS_RUNNING = 2;

    public BridgeClientService()
    {
        super("bridgeclientservice");
    }

    protected void onHandleIntent(Intent intent)
    {
        final ResultReceiver receiver = intent.getParcelableExtra(RECEIVER_KEY);
        receiver.send(STATUS_RUNNING, Bundle.EMPTY);

        int command = intent.getIntExtra(COMMAND_KEY, NONE_COMMAND);
        Bundle b = new Bundle();
        SharedPreferences sharedPref = PreferenceManager.getDefaultSharedPreferences(this);

        switch (command)
        {
            case GET_ASSETS_COMMAND:
                try
                {
                    String server = sharedPref.getString("pref_server", "127.0.0.1");
                    String port = sharedPref.getString("pref_port", "8080");
                    URI bridge_uri =  new URI("http://" + server + ":" + port + "/assets");
                    JSONArray urlArray = new JSONObject(Utility.getURL(bridge_uri)).getJSONArray("asset_urls");

                    String[] assetJSON = new String[urlArray.length()];
                    for (int i = 0; i < urlArray.length(); i++)
                    {
                        assetJSON[i] = Utility.getURL(urlArray.getString(i));
                    }
                    b.putStringArray(RESULTS_KEY, assetJSON);
                    receiver.send(STATUS_GET_ASSETS_FINISHED, b);
                }
                catch (Exception e)
                {
                    b.putString(Intent.EXTRA_TEXT, e.getMessage());
                    receiver.send(STATUS_ERROR, b);
                }
                break;
        }
    }
}
