package com.bridge.bridgeclient;

import android.content.SharedPreferences;

import android.os.Bundle;

import android.preference.PreferenceManager;

import android.widget.ListView;

import android.view.View;
import android.view.ViewGroup;
import android.view.LayoutInflater;

import com.actionbarsherlock.view.Menu;
import com.actionbarsherlock.view.MenuItem;
import com.actionbarsherlock.view.MenuInflater;
import com.actionbarsherlock.app.SherlockFragmentActivity;
import com.actionbarsherlock.app.SherlockListFragment;

public class AssetsFragment extends SherlockListFragment implements SharedPreferences.OnSharedPreferenceChangeListener
{
    AssetsArrayAdapter assetsAdapter;
    ListView devices;
    SharedPreferences preferences;
    SherlockFragmentActivity context;
    boolean refreshing;
    int refreshInterval;

    public AssetsFragment()
    {
        super();
    }

    @Override
    public void onCreate(Bundle savedInstanceState)
    {
        super.onCreate(savedInstanceState);
        setHasOptionsMenu(true);

        context = getSherlockActivity();
        assetsAdapter = new AssetsArrayAdapter(context);
        setListAdapter(assetsAdapter);
        preferences = PreferenceManager.getDefaultSharedPreferences(context);

    }

    @Override
    public void onCreateOptionsMenu(Menu menu, MenuInflater inflater)
    {
        inflater.inflate(R.menu.assetsfragment, menu);
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState)
    {
        View view = inflater.inflate(R.layout.assetsfragment, container);
        refreshing = preferences.getBoolean("pref_auto_refresh", true);
        refreshInterval = Integer.parseInt(preferences.getString("pref_auto_refresh_interval", "4000"));
        if (refreshing)
        {
            assetsAdapter.startRecurringRefresh(refreshInterval);
        }
        preferences.registerOnSharedPreferenceChangeListener(this);

        return view;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item)
    {
        switch (item.getItemId())
        {
            case R.id.menu_refresh_assets:
                assetsAdapter.refresh();
                return true;

            default:
                return super.onOptionsItemSelected(item);
        }
    }

    @Override
    public void onPause()
    {
        if (refreshing)
        {
            assetsAdapter.stopRecurringRefresh();
        }
        preferences.unregisterOnSharedPreferenceChangeListener(this);
        super.onPause();
    }

    @Override
    public void onResume()
    {
        super.onResume();
        preferences.registerOnSharedPreferenceChangeListener(this);
        if (refreshing)
        {
            assetsAdapter.startRecurringRefresh(refreshInterval);
        }
    }

    @Override
    public void onSharedPreferenceChanged(SharedPreferences sharedPreferences, String key)
    {
        if (key.equals("pref_auto_refresh_interval")) 
        {
            refreshInterval = Integer.parseInt(preferences.getString("pref_auto_refresh_interval", "4000"));

            if (refreshing)
            {
                assetsAdapter.stopRecurringRefresh();
                assetsAdapter.startRecurringRefresh(refreshInterval);
            }
        }
        else if (key.equals("pref_auto_refresh"))
        {
            refreshing = preferences.getBoolean("pref_auto_refresh", true);
            
            if (refreshing)
            {
                assetsAdapter.startRecurringRefresh(refreshInterval);
            }
            else
            {
                assetsAdapter.stopRecurringRefresh();
            }
        }
    }
}
