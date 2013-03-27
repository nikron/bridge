package com.bridge.bridgeclient;

import android.content.Context;

import android.view.View;
import android.widget.TableLayout;
import android.widget.TableRow;
import android.widget.TextView;
import android.widget.Button;
import android.widget.Toast;

import java.io.IOException;

class AssetView extends TableLayout
{
    private Context context;
    private Asset asset;

    public AssetView(Context context, Asset asset)
    {
        super(context);
        this.context = context;
        this.asset = asset;

        addView(createRow("Real ID:", asset.getRealID()));
        addView(createRow("UUID:", asset.getUUID()));

        for (int i = 0; i < asset.numberOfCategories(); i++)
            addView(createRow(asset.getCategory(i), asset.getStatus(i)));

        for (int i = 0; i < asset.numberOfActions(); i++)
            addView(createRow(asset.getAction(i)));
    }

    private TableRow createRow(String row1, String row2)
    {
        TableRow row = new TableRow(context);
        TextView row1View = new TextView(context);
        TextView row2View = new TextView(context);

        row1View.setText(row1);
        row2View.setText(row2);

        row.addView(row1View);
        row.addView(row2View);

        return row;
    }

    private TableRow createRow(Action action)
    {
        final Action act = action;
        TableRow row = new TableRow(context);

        Button button = new Button(context);
        button.setText(action.getName());
        button.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) {
                try {
                    act.doAction();
                } catch (IOException e) {
                    Toast.makeText(context, e.getMessage(), Toast.LENGTH_SHORT).show();
                }
            }
        });

        row.addView(button);

        return row;

    }
}
