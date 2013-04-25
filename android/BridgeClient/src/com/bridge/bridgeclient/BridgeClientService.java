package com.bridge.bridgeclient;

import android.os.Bundle;
import android.os.ResultReceiver;
import android.content.Intent;
import android.app.IntentService;

import android.content.SharedPreferences;
import android.preference.PreferenceManager;
import android.view.Window;

import java.net.URI;

import org.json.JSONObject;
import org.json.JSONArray;
import org.json.JSONException;

import java.io.IOException;
import org.apache.http.client.ClientProtocolException;
import java.net.URISyntaxException;

public class BridgeClientService extends IntentService
{
    private static final int PROGRESS_END = Window.PROGRESS_END;

    public static final String COMMAND_KEY = "command";
    public static final String RECEIVER_KEY = "receiver";
    public static final String RESULTS_KEY = "results";
    public static final String PATCH_KEY = "patch";
    public static final String URL_KEY = "url";
    public static final String PROGRESS_KEY = "progress";

    public static final int NONE_COMMAND = 0; //please never use this
    public static final int GET_ASSETS_COMMAND = 1;
    public static final int PATCH_ASSET_COMMAND = 2;

    public static final int STATUS_ERROR = 0;
    public static final int STATUS_GET_ASSETS_FINISHED = 1;
    public static final int STATUS_PROGRESS = 2;
    public static final int STATUS_PATCH_ASSET_FINISHED = 3;
    public static final int STATUS_RUNNING = 3;

    public BridgeClientService()
    {
        super("bridgeclientservice");
    }

    protected void onHandleIntent(Intent intent)
    {

        final ResultReceiver receiver = intent.getParcelableExtra(RECEIVER_KEY);
        Bundle progress = new Bundle();
        progress.putInt(PROGRESS_KEY, 1);
        receiver.send(STATUS_RUNNING, progress);

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

                    progress.putInt(PROGRESS_KEY,  PROGRESS_END / urlArray.length() + 1);
                    receiver.send(STATUS_PROGRESS, progress);

                    for (int i = 0; i < urlArray.length(); i++)
                    {
                        progress.putInt(PROGRESS_KEY,  PROGRESS_END * i / urlArray.length() + 1);
                        receiver.send(STATUS_PROGRESS, progress);
                        assetJSON[i] = Utility.getURL(urlArray.getString(i));
                    }

                    progress.putInt(PROGRESS_KEY,  PROGRESS_END);
                    receiver.send(STATUS_PROGRESS, progress);
                    b.putStringArray(RESULTS_KEY, assetJSON);
                    receiver.send(STATUS_GET_ASSETS_FINISHED, b);
                }
                catch (Exception e)
                {
                    b.putString(Intent.EXTRA_TEXT, e.getMessage());
                    receiver.send(STATUS_ERROR, b);
                }
                break;

            case PATCH_ASSET_COMMAND:
                try
                {
                    progress.putInt(PROGRESS_KEY,  PROGRESS_END / 2);
                    receiver.send(STATUS_PROGRESS, progress);

                    Utility.patchURL(intent.getStringExtra(URL_KEY), intent.getStringExtra(PATCH_KEY));

                    progress.putInt(PROGRESS_KEY,  PROGRESS_END);
                    receiver.send(STATUS_PROGRESS, progress);
                    receiver.send(STATUS_PATCH_ASSET_FINISHED, b);
                }
                catch (Exception e)
                {
                    b.putString(Intent.EXTRA_TEXT, e.getMessage());
                    receiver.send(STATUS_ERROR, b);
                }
        }
    }
}
