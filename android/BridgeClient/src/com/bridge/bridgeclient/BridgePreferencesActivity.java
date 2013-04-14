package com.bridge.bridgeclient;

import android.os.Bundle;
import com.actionbarsherlock.app.SherlockPreferenceActivity;

public class BridgePreferencesActivity extends SherlockPreferenceActivity
{
    @Override
    public void onCreate(Bundle savedInstanceState)
    {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.preferences);
    }
}
