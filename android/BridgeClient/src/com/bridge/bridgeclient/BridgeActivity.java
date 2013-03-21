package com.bridge.bridgeclient;

import android.app.Activity;
import android.content.Context;

import android.os.Bundle;

import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.ListView;
import android.widget.ArrayAdapter;
import android.widget.Toast;

import org.apache.http.HttpEntity;
import org.apache.http.HttpResponse;
import org.apache.http.StatusLine;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.impl.client.DefaultHttpClient;

import org.json.JSONObject;
import org.json.JSONArray;
import org.json.JSONException;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;

public class BridgeActivity extends Activity
{
    /** Called when the activity is first created. */
    @Override
    public void onCreate(Bundle savedInstanceState)
    {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.main);

        final Button create_device = (Button) findViewById(R.id.create_device);

        final ListView devices = (ListView) findViewById(R.id.devices);
        final ArrayAdapter<String> deviceAdapter = new ArrayAdapter<String>(this, R.layout.list_item, R.id.listitem);
        devices.setAdapter(deviceAdapter);


        final Button refreshDevices = (Button) findViewById(R.id.refresh);
        refreshDevices.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) {
                updateDeviceListView(deviceAdapter);
            }
        });
    }

    private void updateDeviceListView(ArrayAdapter<String> adapter)
    {
        try {
            String assets = getURL("http://192.168.0.198:8080/assets");
            JSONObject obj = new JSONObject(assets);
            JSONArray urlArray = obj.optJSONArray("assets_urls");

            adapter.clear();
            for (int i = 0; i < urlArray.length(); i++)
            {
                adapter.add(urlArray.getString(i));
            }

        } catch (JSONException e) {
            Toast.makeText(this, e.getMessage(), Toast.LENGTH_SHORT).show();
        }
    }

    private String getURL(String url)
    {
        StringBuilder builder = new StringBuilder();
        HttpClient client = new DefaultHttpClient();
        HttpGet get = new HttpGet(url);

        try {
            HttpResponse response = client.execute(get);
            StatusLine status = response.getStatusLine();
            HttpEntity entity = response.getEntity();
            InputStream content = entity.getContent();
            BufferedReader reader = new BufferedReader(new InputStreamReader(content));

            String line;
            while ((line = reader.readLine()) != null) {
                builder.append(line);
            }

        } catch (ClientProtocolException e) {
            Toast.makeText(this, e.getMessage(), Toast.LENGTH_SHORT).show();
        } catch (IOException e) {
            Toast.makeText(this, e.getMessage(), Toast.LENGTH_SHORT).show();
        }

        return builder.toString();
    }
}
