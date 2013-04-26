package com.bridge.bridgeclient;

import android.app.Dialog;
import android.app.AlertDialog;
import android.os.Bundle;

import com.actionbarsherlock.app.SherlockDialogFragment;

public class SaveBridgeModelDialogFragment extends SherlockDialogFragment
{
    @Override
    public Dialog onCreateDialog(Bundle savedInstanceState)
    {
        return new AlertDialog.Builder(getSherlockActivity())
            .setTitle(R.string.save_dialog_title)
            .setPositiveButton(R.string.save_dialog_save, null)
            .setNegativeButton(R.string.save_dialog_cancel, null)
            .create();
    }
}
