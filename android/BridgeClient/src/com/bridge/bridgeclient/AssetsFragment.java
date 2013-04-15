package com.bridge.bridgeclient;

import com.actionbarsherlock.app.SherlockFragment;
import com.actionbarsherlock.view.Menu;
import com.actionbarsherlock.view.MenuItem;
import com.actionbarsherlock.view.MenuInflater;

import android.content.SharedPreferences;
import android.preference.PreferenceManager;

import android.os.Bundle;
import android.view.View;
import android.view.ViewGroup;
import android.view.LayoutInflater;
import android.widget.ExpandableListView;

import android.widget.Toast;

import java.net.URI;
import java.net.URISyntaxException;

public class AssetsFragment extends SherlockFragment
{
    URI serverURL;
    AssetExpandableListAdapter deviceAdapter;
    SharedPreferences sharedPref;
    AssetList assetList;

    public AssetsFragment()
    {
        super();
        this.serverURL = null;
        this.assetList = new AssetList(serverURL);
    }

    @Override
    public void onCreate(Bundle savedInstanceState)
    {
        super.onCreate(savedInstanceState);
        setHasOptionsMenu(true);
        this.sharedPref = PreferenceManager.getDefaultSharedPreferences(getActivity());
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState)
    {
        View view = inflater.inflate(R.layout.assetsfragment, container);
        final ExpandableListView devices = (ExpandableListView) view.findViewById(R.id.expandassetlist);
        deviceAdapter = new AssetExpandableListAdapter(getActivity(), this.assetList);
        devices.setAdapter(deviceAdapter);

        return view;
    }

    @Override
    public void onCreateOptionsMenu(Menu menu, MenuInflater inflater) {
        inflater.inflate(R.menu.assetsfragment, menu);
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item)
    {
        switch (item.getItemId())
        {
            case R.id.menu_refresh_assets:
                refresh();
                return true;
            default:
                return super.onOptionsItemSelected(item);
        }
    }

    private void displayError(String message)
    {
    }

    private void refresh()
    {
        String server = sharedPref.getString("pref_server", "");
        String port = sharedPref.getString("pref_port", "8080");
        URI url;

        try
        {
            url = new URI(server + ":" + port + "/assets");
            this.assetList.setURL(url);
        }
            catch (URISyntaxException e)
        {
            displayError(e.getMessage());
        }

        deviceAdapter.refresh();
    }
}
