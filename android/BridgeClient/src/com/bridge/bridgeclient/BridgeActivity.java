package com.bridge.bridgeclient;

import android.content.Context;
import android.content.Intent;

import android.os.Bundle;

import com.actionbarsherlock.view.Menu;
import com.actionbarsherlock.view.MenuItem;
import com.actionbarsherlock.view.MenuInflater;
import com.actionbarsherlock.app.SherlockFragmentActivity;
import android.support.v4.app.FragmentManager;
import com.actionbarsherlock.view.Window;

public class BridgeActivity extends SherlockFragmentActivity
{
    /** Called when the activity is first created. */
    @Override
    public void onCreate(Bundle savedInstanceState)
    {
        requestWindowFeature(Window.FEATURE_PROGRESS);
        super.onCreate(savedInstanceState);
        setContentView(R.layout.main);
        setSupportProgressBarVisibility(false);
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu)
    {
        MenuInflater inflater = getSupportMenuInflater();
        inflater.inflate(R.menu.menu, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item)
    {
        switch (item.getItemId())
        {
            case R.id.menu_pref:
                startActivity(new Intent(this, BridgePreferencesActivity.class));
                return true;

            case R.id.menu_save:
                SaveBridgeModelDialogFragment frag = new SaveBridgeModelDialogFragment();
                frag.show(getSupportFragmentManager(), "dialog");
                return true;

            default:
                return super.onOptionsItemSelected(item);
        }
    }
}
