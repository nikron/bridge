package com.bridge.bridgeclient;

import android.content.Context;
import android.content.Intent;

import android.os.Bundle;

import android.view.View;
import com.actionbarsherlock.view.Menu;
import com.actionbarsherlock.view.MenuItem;
import com.actionbarsherlock.view.MenuInflater;
import com.actionbarsherlock.app.SherlockFragmentActivity;

public class BridgeActivity extends SherlockFragmentActivity
{
    /** Called when the activity is first created. */
    @Override
    public void onCreate(Bundle savedInstanceState)
    {
        setTheme(R.style.Theme_Sherlock);
        super.onCreate(savedInstanceState);
        setContentView(R.layout.main);
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        MenuInflater inflater = getSupportMenuInflater();
        inflater.inflate(R.menu.settings, menu);
        return true;
    }

    public boolean launchPreferences(MenuItem menu) {
        startActivity(new Intent(this, BridgePreferencesActivity.class));
        return true;
    }
}
