package com.bridge.bridgeclient;

import android.content.Intent;
import android.content.Context;

import android.os.Bundle;
import android.os.Handler;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;

import android.widget.ArrayAdapter;
import android.widget.CompoundButton;
import android.widget.RelativeLayout;
import android.widget.TextView;
import android.widget.Toast;

import com.actionbarsherlock.app.SherlockFragmentActivity;

import org.jraf.android.backport.switchwidget.Switch;
//import android.widget.Switch;

import org.json.JSONException;

public class AssetsArrayAdapter extends ArrayAdapter<Asset> implements BridgeClientReceiver.Receiver
{
    final SherlockFragmentActivity context;
    BridgeClientReceiver receiver;

    static final int binaryAsset = R.xml.asset_binary;
    static final int rangeAsset = R.xml.asset_range;
    static final int unknownAsset = R.xml.asset_unknown;
    static final int textViewResourceId = R.id.assetname;
    static final int controlResourceId = R.id.assetcontrol;

    public AssetsArrayAdapter(SherlockFragmentActivity context)
    {
        super(context, binaryAsset, textViewResourceId);
        this.context = context;

        receiver = new BridgeClientReceiver(new Handler());
        receiver.setReceiver(this);
    }

    @Override
    public View getView (int position, View convertView, ViewGroup parent)
    {
        final Asset asset = getItem(position);
        RelativeLayout layout;

        switch (asset.getMainType())
        {
            case State.BINARY_TYPE:
                layout = (RelativeLayout) LayoutInflater.from(context).inflate(binaryAsset, parent, false);
                Switch mainSwitch = (Switch) layout.findViewById(controlResourceId);;
                mainSwitch.setEnabled(asset.isMainEnabled());
                mainSwitch.setChecked(asset.getCurrentMainState());
                mainSwitch.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
                    public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                        String message = asset.setCurrentMainState(isChecked);
                        sendAssetPatch(asset.getURL(), message);
                }});

                break;

            default:
                layout = (RelativeLayout) LayoutInflater.from(context).inflate(unknownAsset, parent, false);
                break;
        }

        TextView assetName = (TextView) layout.findViewById(textViewResourceId);
        assetName.setText(asset.toString());

        return layout;
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

    private void sendAssetPatch(String url, String patch)
    {
        final Intent intent = new Intent(Intent.ACTION_SYNC, null, context, BridgeClientService.class);
        intent.putExtra(BridgeClientService.RECEIVER_KEY, receiver);
        intent.putExtra(BridgeClientService.COMMAND_KEY, BridgeClientService.PATCH_ASSET_COMMAND);
        intent.putExtra(BridgeClientService.URL_KEY, url);
        intent.putExtra(BridgeClientService.PATCH_KEY, patch);

        context.startService(intent);
    }

    private void displayError(String message)
    {
        Toast toast = Toast.makeText(context, message, Toast.LENGTH_SHORT);
        toast.show();
    }
}
