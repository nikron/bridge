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
    public static final String COMMAND_KEY = "command";
    public static final String RECEIVER_KEY = "receiver";
    public static final String RESULTS_KEY = "results";
    public static final String PATCH_KEY = "patch";
    public static final String URL_KEY = "url";
    public static final String PROGRESS_KEY = "progress";

    public static final int NONE_COMMAND = 0; //please never use this
    public static final int GET_ASSETS_COMMAND = 1;
    public static final int GET_BRIDGE_INFO_COMMAND = 3;
    public static final int PATCH_ASSET_COMMAND = 2;

    public static final int STATUS_RUNNING = 1;
    public static final int STATUS_PROGRESS = 2;
    public static final int STATUS_ERROR = 3;

    public static final int STATUS_GET_ASSETS_FINISHED = 4;
    public static final int STATUS_GET_BRIDGE_INFO_FINISHED = 6;
    public static final int STATUS_PATCH_ASSET_FINISHED = 5;


    public BridgeClientService()
    {
        super("bridgeclientservice");
    }

    protected void onHandleIntent(Intent intent)
    {

        final ResultReceiver receiver = intent.getParcelableExtra(RECEIVER_KEY);
        receiver.send(STATUS_RUNNING, Bundle.EMPTY);

        int command = intent.getIntExtra(COMMAND_KEY, NONE_COMMAND);
        switch (command)
        {
            case GET_ASSETS_COMMAND:
                getAssets(receiver);
                break;

            case GET_BRIDGE_INFO_COMMAND:
                try
                {
                    sendProgress(receiver, 1, 2);
                    String info = Utility.getURL(getBridgeURI(""));
                    sendProgress(receiver, 2, 2);

                    Bundle bundle = new Bundle();
                    bundle.putString(Intent.EXTRA_TEXT, info);
                    receiver.send(STATUS_GET_BRIDGE_INFO_FINISHED, Bundle.EMPTY);
                }
                catch (Exception e)
                {
                    sendError(receiver, e);
                }
                break;

            case PATCH_ASSET_COMMAND:
                try
                {
                    sendProgress(receiver, 1, 2);

                    Utility.patchURL(intent.getStringExtra(URL_KEY), intent.getStringExtra(PATCH_KEY));

                    sendProgress(receiver, 2, 2);
                    receiver.send(STATUS_PATCH_ASSET_FINISHED, Bundle.EMPTY);
                }
                catch (Exception e)
                {
                    sendError(receiver, e);
                }
        }
    }

    private void getAssets(ResultReceiver receiver)
    {
        try
        {
            Bundle bundle = new Bundle();
            URI uri = getBridgeURI("/assets");
            JSONArray urlArray = new JSONObject(Utility.getURL(uri)).getJSONArray("asset_urls");

            int length = urlArray.length();
            String[] assetJSON = new String[length];

            sendProgress(receiver, 1, length + 1);

            for (int i = 0; i < length; i++)
            {
                assetJSON[i] = Utility.getURL(urlArray.getString(i));
                sendProgress(receiver, i + 2, length + 1);
            }

            bundle.putStringArray(RESULTS_KEY, assetJSON);
            receiver.send(STATUS_GET_ASSETS_FINISHED, bundle);
        }
        catch (Exception e)
        {
            sendError(receiver, e);
        }
    }

    private URI getBridgeURI(String append) throws URISyntaxException
    {
        SharedPreferences sharedPref = PreferenceManager.getDefaultSharedPreferences(this);
        String server = sharedPref.getString("pref_server", "127.0.0.1");
        String port = sharedPref.getString("pref_port", "8080");
        URI bridge_uri =  new URI("http://" + server + ":" + port + append);
        return bridge_uri;
    }

    private void sendError(ResultReceiver receiver, Exception e)
    {
        Bundle bundle = new Bundle();
        bundle.putString(Intent.EXTRA_TEXT, e.getMessage());
        receiver.send(STATUS_ERROR, bundle);
    }

    private void sendProgress(ResultReceiver receiver, int progress, int end)
    {
        Bundle bundle = new Bundle();
        int shift = progress / end * Window.PROGRESS_END + Window.PROGRESS_START;
        bundle.putInt(PROGRESS_KEY,  shift);
        receiver.send(STATUS_PROGRESS, bundle);
    }
}
