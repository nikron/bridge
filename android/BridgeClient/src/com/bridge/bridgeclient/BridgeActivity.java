package com.bridge.bridgeclient;

import android.content.Context;
import android.content.Intent;

import android.os.Bundle;
import android.os.Handler;

import android.widget.Toast;

import com.actionbarsherlock.view.Menu;
import com.actionbarsherlock.view.MenuItem;
import com.actionbarsherlock.view.MenuInflater;
import com.actionbarsherlock.app.SherlockFragmentActivity;
import android.support.v4.app.FragmentManager;
import com.actionbarsherlock.view.Window;

public class BridgeActivity extends SherlockFragmentActivity implements BridgeClientReceiver.Receiver
{
    BridgeClientReceiver receiver;

    /** Called when the activity is first created. */
    @Override
    public void onCreate(Bundle savedInstanceState)
    {
        requestWindowFeature(Window.FEATURE_PROGRESS);
        super.onCreate(savedInstanceState);
        setContentView(R.layout.main);
        setSupportProgressBarVisibility(false);


        receiver = new BridgeClientReceiver(new Handler());
        receiver.setReceiver(this);
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
                final Intent intent = new Intent(Intent.ACTION_SYNC, null, this, BridgeClientService.class);
                intent.putExtra(BridgeClientService.RECEIVER_KEY, receiver);
                intent.putExtra(BridgeClientService.COMMAND_KEY, BridgeClientService.GET_BRIDGE_INFO_COMMAND);
                startService(intent);

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
                break;

            case BridgeClientService.STATUS_PROGRESS:
                break;

            case BridgeClientService.STATUS_ERROR:
                String error = resultData.getString(Intent.EXTRA_TEXT);
                Toast toast = Toast.makeText(this, error, Toast.LENGTH_SHORT);
                toast.show();
                break;

            case BridgeClientService.STATUS_GET_BRIDGE_INFO_FINISHED:
                BridgeSaveModelDialogFragment frag = new BridgeSaveModelDialogFragment();
                frag.show(getSupportFragmentManager(), "savemodel");
                break;

            default:
                break;
        }
    }
}
