package com.bridge.bridgeclient;

import android.content.Context;

import android.os.Bundle;

import android.view.View;
import com.actionbarsherlock.view.Menu;
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
}
