package com.app.client;

import android.os.Bundle;
import android.support.v4.view.ViewPager;
import android.support.v7.app.AppCompatActivity;
import android.widget.Adapter;


public class QuestionActivity extends AppCompatActivity {
    Adpater adapter;
    ViewPager viewPager;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_question);
        // 아까 만든 view
        viewPager = (ViewPager)findViewById(R.id.view);
        //adapter 초기화
        adapter = new Adpater(this);
        viewPager.setAdapter(adapter);
    }
}
