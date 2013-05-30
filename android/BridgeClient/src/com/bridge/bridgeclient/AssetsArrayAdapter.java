package com.bridge.bridgeclient;

import android.content.Intent;
import android.content.Context;

import android.os.Bundle;
import android.os.Handler;

import android.view.View;
import android.view.ViewGroup;

import android.widget.ArrayAdapter;
import android.widget.TextView;
import android.widget.Toast;

import com.actionbarsherlock.app.SherlockFragmentActivity;

import org.json.JSONException;

public class AssetsArrayAdapter extends ArrayAdapter<Asset> implements BridgeClientReceiver.Receiver, BriefAssetViewFactory.PatchHandler
{
    final SherlockFragmentActivity context;
    BridgeClientReceiver receiver;
    Handler handler;

    public AssetsArrayAdapter(SherlockFragmentActivity context)
    {
        super(context, R.xml.asset_unknown, R.id.assetname);
        this.context = context;
        handler = new Handler();
        receiver = new BridgeClientReceiver(handler);
        receiver.setReceiver(this);
    }

    @Override
    public View getView (int position, View convertView, ViewGroup parent)
    {
        //TODO: Use asset type rather than mainstate type
        Asset asset = getItem(position);
        State mainState = asset.getMainState();

        if (mainState != null)
        {
            switch (mainState.getType())
            {
                case State.BINARY_TYPE:
                    return new BriefBinaryAssetViewFactory(context, asset, this).getView();

                case State.RANGE_TYPE:
                    return new BriefRangeAssetViewFactory(context, asset, this).getView();

                default:
                    return new BriefAssetViewFactory(context, asset, this).getView();
            }
        }
        return new BriefAssetViewFactory(context, asset, this).getView();
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
                clear();
                break;

            default:
                context.setSupportProgressBarVisibility(false);
                break;
        }
    }

    public void refresh()
    {
        final Intent intent = new Intent(Intent.ACTION_SYNC, null, context, BridgeClientService.class);
        intent.putExtra(BridgeClientService.RECEIVER_KEY, receiver);
        intent.putExtra(BridgeClientService.COMMAND_KEY, BridgeClientService.GET_ASSETS_COMMAND);

        context.startService(intent);
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

    public void startRecurringRefresh(int interval)
    {
        final int inter = interval;
        refresh();
        handler.postDelayed(new Runnable() {
            public void run() {
                startRecurringRefresh(inter);
            }
        }, inter);
    }

    public void stopRecurringRefresh()
    {
        handler.removeCallbacksAndMessages(null);
    }

    private void displayError(String message)
    {
        Toast toast = Toast.makeText(context, message, Toast.LENGTH_SHORT);
        toast.show();
    }


    private void newAssetData(String[] assetsJSON)
    {
        clear();
        for (int i = 0; i < assetsJSON.length; i++)
        {
            try
            {
                add(new Asset(assetsJSON[i]));
            }
            catch (JSONException e)
            {
                displayError(e.getMessage());
            }
        }

        notifyDataSetChanged();
    }
}
