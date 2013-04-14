package com.bridge.bridgeclient;

import android.app.Activity;
import android.content.Context;

import android.os.Bundle;

import android.view.View;
import android.view.Menu;
import android.view.MenuInflater;

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
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        MenuInflater inflater = getMenuInflater();
        inflater.inflate(R.menu.menu, menu);
        return true;
    }
}
