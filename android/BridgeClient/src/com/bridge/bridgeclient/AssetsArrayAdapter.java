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
import android.widget.SeekBar;
//import android.widget.Switch;

import org.json.JSONException;

public class AssetsArrayAdapter extends ArrayAdapter<Asset> implements BridgeClientReceiver.Receiver
{
    final SherlockFragmentActivity context;
    BridgeClientReceiver receiver;
    private Handler handler;

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
        final Asset asset = getItem(position);
        final State mainState = asset.getMainState();
        RelativeLayout layout;

        if (mainState != null)
        {
            switch (mainState.getType())
            {
                case State.BINARY_TYPE:
                    layout = (RelativeLayout) LayoutInflater.from(context).inflate(R.xml.asset_binary, parent, false);
                    Switch mainSwitch = (Switch) layout.findViewById(R.id.assetcontrol);
                    mainSwitch.setEnabled(mainState.isEnabled());
                    mainSwitch.setChecked(mainState.getCurrent());
                    mainSwitch.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
                        public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                            String message = mainState.setState(isChecked);
                            sendAssetPatch(asset.getURL(), message);
                        }});
                    break;

                case State.RANGE_TYPE:
                    layout = (RelativeLayout) LayoutInflater.from(context).inflate(R.xml.asset_range, parent, false);
                    SeekBar mainSeekBar = (SeekBar) layout.findViewById(R.id.assetcontrol);
                    mainSeekBar.setEnabled(mainState.isEnabled());
                    mainSeekBar.setMax(mainState.getMax() - mainState.getMin());
                    mainSeekBar.setProgress(mainState.getCurrentInt());
                    mainSeekBar.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
                        public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                            String message = mainState.setState(progress + mainState.getMin());
                            sendAssetPatch(asset.getURL(), message);
                        }
                        public void onStartTrackingTouch(SeekBar seekBar) {
                        }
                        public void onStopTrackingTouch(SeekBar seekBar) {
                        }
                    });
                    break;

                default:
                    layout = (RelativeLayout) LayoutInflater.from(context).inflate(R.xml.asset_unknown, parent, false);
                    break;
            }
        }
        else
        {
            layout = (RelativeLayout) LayoutInflater.from(context).inflate(R.xml.asset_unknown, parent, false);
        }

        TextView assetName = (TextView) layout.findViewById(R.id.assetname);
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

    public void start_recurring_refresh()
    {
        handler.postDelayed(new Runnable() {
            public void run() {
                refresh();
                start_recurring_refresh();
            }
        }, 2000);
    }

    public void stop_recurring_refresh()
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

    private void sendAssetPatch(String url, String patch)
    {
        final Intent intent = new Intent(Intent.ACTION_SYNC, null, context, BridgeClientService.class);
        intent.putExtra(BridgeClientService.RECEIVER_KEY, receiver);
        intent.putExtra(BridgeClientService.COMMAND_KEY, BridgeClientService.PATCH_ASSET_COMMAND);
        intent.putExtra(BridgeClientService.URL_KEY, url);
        intent.putExtra(BridgeClientService.PATCH_KEY, patch);

        context.startService(intent);
    }
}
