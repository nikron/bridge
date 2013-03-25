package com.bridge.bridgeclient;

import android.app.Activity;
import android.content.Context;

import android.os.Bundle;

import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.ExpandableListView;
import android.widget.Toast;

public class BridgeActivity extends Activity
{
    /** Called when the activity is first created. */
    @Override
    public void onCreate(Bundle savedInstanceState)
    {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.main);

        final Button create_device = (Button) findViewById(R.id.create_device);

        final ExpandableListView devices = (ExpandableListView) findViewById(R.id.devices);
        final AssetExpandableListAdapter deviceAdapter = new AssetExpandableListAdapter(this);
        devices.setGroupIndicator(null);
        devices.setAdapter(deviceAdapter);


        final Button refreshDevices = (Button) findViewById(R.id.refresh);
        refreshDevices.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) {
                deviceAdapter.refresh();
            }
        });
    }
}
