package com.bridge.bridgeclient;

import android.content.Context;


import android.view.View;
import android.widget.TableLayout;
import android.widget.TableRow;
import android.widget.TextView;
import android.widget.Button;

class AssetView extends TableLayout
{
    private Context context;
    public String name;
    public String realID;
    public String url;
    public String uuid;
    public String[][] status;
    public Action[] actions;

    public AssetView(Context context, String url, String name, String realID, String[][] status, String uuid, Action[] actions)
    {
        super(context);

        this.context = context;

        this.name = name;
        this.realID = realID;
        this.uuid = uuid;
        this.url = url;

        this.status = status;
        this.actions = actions;

        addView(createRow("Real ID:", realID));
        addView(createRow("UUID:", uuid));

        for (int i = 0; i < status.length; i++)
            addView(createRow(status[i][0], status[i][1]));

        for (int i = 0; i < actions.length; i++)
            addView(createRow(actions[i]));
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
                act.doAction();
            }
        });

        row.addView(button);

        return row;

    }
}
