package com.bridge.bridgeclient;

import com.actionbarsherlock.app.SherlockFragmentActivity;
import com.actionbarsherlock.app.SherlockListFragment;
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

public class AssetsFragment extends SherlockListFragment implements BridgeClientReceiver.Receiver
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

        context = getSherlockActivity();
        assetsAdapter = new AssetsArrayAdapter(context, this);
        setListAdapter(assetsAdapter);

        receiver = new BridgeClientReceiver(new Handler());
        receiver.setReceiver(this);
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState)
    {
        View view = inflater.inflate(R.layout.assetsfragment, container);

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
                context.setSupportProgressBarVisibility(true);
                break;

            case BridgeClientService.STATUS_PROGRESS:
                context.setSupportProgress(resultData.getInt(BridgeClientService.PROGRESS_KEY));
                break;

            case BridgeClientService.STATUS_GET_ASSETS_FINISHED:
                context.setSupportProgressBarVisibility(false);
                newAssetData(resultData.getStringArray(BridgeClientService.RESULTS_KEY));
                break;

            case BridgeClientService.STATUS_ERROR:
                context.setSupportProgressBarVisibility(false);
                displayError(resultData.getString(Intent.EXTRA_TEXT));
                assetsAdapter.clear();
                break;

            default:
                context.setSupportProgressBarVisibility(false);
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
                assetsAdapter.add(new Asset(assetsJSON[i]));
            }
                catch (JSONException e)
            {
                displayError(e.getMessage());
            }
        }

        assetsAdapter.notifyDataSetChanged();
    }

    public void sendAssetPatch(String url, String patch)
    {
        final Intent intent = new Intent(Intent.ACTION_SYNC, null, context, BridgeClientService.class);
        intent.putExtra(BridgeClientService.RECEIVER_KEY, receiver);
        intent.putExtra(BridgeClientService.COMMAND_KEY, BridgeClientService.PATCH_ASSET_COMMAND);
        intent.putExtra(BridgeClientService.URL_KEY, url);
        intent.putExtra(BridgeClientService.PATCH_KEY, patch);

        context.startService(intent);
    }

    private void refresh()
    {
        final Intent intent = new Intent(Intent.ACTION_SYNC, null, context, BridgeClientService.class);
        intent.putExtra(BridgeClientService.RECEIVER_KEY, receiver);
        intent.putExtra(BridgeClientService.COMMAND_KEY, BridgeClientService.GET_ASSETS_COMMAND);

        context.startService(intent);
    }
}
