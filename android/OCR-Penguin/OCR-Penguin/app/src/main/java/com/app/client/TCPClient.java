package com.app.client;

import android.content.Context;
import android.util.Log;
import android.widget.Toast;

import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.net.Socket;
import java.text.SimpleDateFormat;
import java.util.Date;

import static com.app.client.CameraOverView.*;

public class TCPClient implements Runnable { // 소켓 통신
    private String filePath;
    private String serverIP;
    private int serverPort;
    private String timeStamp = new SimpleDateFormat("yyyyMMdd_HHmmss").format(new Date());
    private String fileName = timeStamp + "result.xlsx";
    private String FileSize;
    private Context context;
    private CameraOverView cameraOverView;
    private boolean taskflag;

    public TCPClient(String filePath, String ip, int port, boolean taskflag, Context context) {
        super();
        this.serverIP = ip;
        this.serverPort = port;
        this.filePath = filePath;
        this.taskflag = taskflag;
        this.context = context;
    }
// 일단 건너 뛰어 ㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋ 해결하고싶엌ㅋㅋㅋ 5뷴먼 더해봄 20분까지 못하면 주석 ㄱ 되는건가? 아닌듯 해바
/*    public void ThreadToast(final String message){
        cameraOverView.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                Toast.makeText(context, message, Toast.LENGTH_SHORT)
                        .show();
            }

        });
    }*/

    @Override
    public void run() {
        try {
            taskflag = false;
            Log.d("Wait", "대기중");
            Socket sock = new Socket(this.serverIP, this.serverPort);
            DataInputStream dis = new DataInputStream(new FileInputStream(new File(this.filePath)));
            //Log.d(this.filePath, "파일 경로");
            DataOutputStream dos = new DataOutputStream(sock.getOutputStream());
            byte[] buf = new byte[1024];

            //while (true) {
                Log.d("connecting", "발신중...");
                try {
                    //loading();
                    while (dis.read(buf) > 0) {
                        dos.write(buf);
                        dos.flush();
                    }
                    Log.d("finish", "발신 완료!!!!.");
                    sock.shutdownOutput();
                } catch (Exception e) {
                    taskflag = true;
                    //ThreadToast("문서 사진이 아닙니다");
                    Log.d("Error", "1. 문서 사진이 아닙니다");
                    e.printStackTrace();
                }
                try {
                    File root = android.os.Environment.getExternalStorageDirectory();
                    File dir = new File(root.getAbsolutePath() + "/pth/excel/");
                    if (dir.exists() == false) {
                        dir.mkdirs();
                    }
                    //Log.d(TAG, fileName);
                    byte[] tmpByte = new byte[1024];
                    dis = new DataInputStream(sock.getInputStream()); //InputStream 확장
                    File file = new File(dir, fileName);
                    FileOutputStream fos = new FileOutputStream(file);
                    int Read;
                    for (; ; ) {
                        Read = dis.read(tmpByte); // 쩃든 지금자맘남잠자만 우리 내일 만남?
                    taskflag = true;
                    dis.close();
                    fos.close();
                    sock.close();
                    long lFileSize = file.length();
                    FileSize = Long.toString(lFileSize);
                    int numFS = Integer.parseInt(FileSize);
                    //Log.d(TAG,FileSize);
                    if (numFS > 10) {
                        //ThreadToast("엑셀로 변환 완료!");
                    } else {
                        file.delete();
                        //ThreadToast("문서 사진으로 인식 되지 않습니다");
                    }
                } catch (Exception e) {
                    taskflag = true;
                    //ThreadToast("문서 사진이 아닙니다");
                    Log.d("Error", "2. 문서 사진이 아닙니다");
                    e.printStackTrace();
                }
            } catch(Exception e){
                taskflag = true;
                //ThreadToast("문서 사진이 아닙니다");
                Log.d("Error","3. 문서 사진이 아닙니다.");
                e.printStackTrace();
        }
    }
}
