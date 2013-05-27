package com.bridge.bridgeclient;

import android.os.Bundle;

import android.view.View;
import android.view.ViewGroup;
import android.view.LayoutInflater;
import android.widget.ListView;

import com.actionbarsherlock.app.SherlockFragmentActivity;
import com.actionbarsherlock.app.SherlockListFragment;
import com.actionbarsherlock.view.Menu;
import com.actionbarsherlock.view.MenuItem;
import com.actionbarsherlock.view.MenuInflater;

public class AssetsFragment extends SherlockListFragment
{
    SherlockFragmentActivity context;
    AssetsArrayAdapter assetsAdapter;
    ListView devices;

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
        assetsAdapter.start_recurring_refresh();
        assetsAdapter.refresh();
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
        assetsAdapter.stop_recurring_refresh();
        super.onPause();
    }

    @Override
    public void onResume()
    {
        super.onResume();
        assetsAdapter.start_recurring_refresh();
    }
}
