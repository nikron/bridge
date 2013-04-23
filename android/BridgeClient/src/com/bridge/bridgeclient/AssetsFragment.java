package com.bridge.bridgeclient;

import com.actionbarsherlock.app.SherlockFragmentActivity;
import com.actionbarsherlock.app.SherlockFragment;
import com.actionbarsherlock.view.Menu;
import com.actionbarsherlock.view.MenuItem;
import com.actionbarsherlock.view.MenuInflater;

import android.os.Bundle;
import android.os.Handler;

import android.content.Intent;

import android.view.View;
import android.view.ViewGroup;
import android.view.LayoutInflater;
import android.widget.ListView;
import android.widget.Toast;

import org.json.JSONException;

public class AssetsFragment extends SherlockFragment implements BridgeClientReceiver.Receiver
{
    SherlockFragmentActivity context;
    BridgeClientReceiver receiver;
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
        receiver = new BridgeClientReceiver(new Handler());
        receiver.setReceiver(this);

        context = getSherlockActivity();
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState)
    {
        View view = inflater.inflate(R.layout.assetsfragment, container);
        devices = (ListView) view.findViewById(R.id.assetlist);
        assetsAdapter = new AssetsArrayAdapter(context, R.xml.asset, R.id.assetname);
        devices.setAdapter(assetsAdapter);

        return view;
    }

    @Override
    public void onCreateOptionsMenu(Menu menu, MenuInflater inflater)
    {
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

    @Override
    public void onReceiveResult(int resultCode, Bundle resultData)
    {
        switch (resultCode)
        {
            case BridgeClientService.STATUS_RUNNING:
                context.setSupportProgressBarIndeterminateVisibility(true);
                break;

            case BridgeClientService.STATUS_GET_ASSETS_FINISHED:
                context.setSupportProgressBarIndeterminateVisibility(false);
                newAssetData(resultData.getStringArray(BridgeClientService.RESULTS_KEY));

                break;
            
            case BridgeClientService.STATUS_ERROR:
                context.setSupportProgressBarIndeterminateVisibility(false);
                displayError(resultData.getString(Intent.EXTRA_TEXT));
                break;
        }
    }

    private void displayError(String message)
    {
        Toast toast = Toast.makeText(context, message, Toast.LENGTH_SHORT);
        toast.show();
    }

    private void newAssetData(String[] assetsJSON)
    {
        assetsAdapter.clear();
        for (int i = 0; i < assetsJSON.length; i++)
        {
            try
            {
                Toast toast = Toast.makeText(context, new Asset(assetsJSON[i]).toString(), Toast.LENGTH_SHORT);
                toast.show();
                assetsAdapter.add(new Asset(assetsJSON[i]));
            }
                catch (JSONException e)
            {
                displayError(e.getMessage());
            }
        }

        assetsAdapter.notifyDataSetChanged();
    }

    private void refresh()
    {
        final Intent intent = new Intent(Intent.ACTION_SYNC, null, context, BridgeClientService.class);
        intent.putExtra(BridgeClientService.RECEIVER_KEY, receiver);
        intent.putExtra(BridgeClientService.COMMAND_KEY, BridgeClientService.GET_ASSETS_COMMAND);

        context.startService(intent);
    }
}
