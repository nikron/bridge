package com.bridge.bridgeclient;

import android.os.Bundle;
import com.actionbarsherlock.app.SherlockPreferenceActivity;

public class BridgePreferencesActivity extends SherlockPreferenceActivity
{
    @Override
    public void onCreate(Bundle savedInstanceState)
    {
        setTheme(R.style.Theme_Sherlock);
        super.onCreate(savedInstanceState);
        addPreferencesFromResource(R.xml.preferences);
    }
}
