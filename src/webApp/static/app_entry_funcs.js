//ランニング記録のエントリー
const entry_runData = async() => {
    yyyy = document.getElementById("yyyy").value;
    dd = document.getElementById("dd").value;
    mm = document.getElementById("mm").value;
    distance = document.getElementById("distance").value;
    condition = document.getElementById("condition").value;
    runningDist = document.getElementById("runningDist").value;

    querys = {
        "yyyy" : yyyy,
        "dd" : dd,
        "mm" : mm,
        "distance" : distance,
        "condition" : condition,
        "runningDist" : runningDist
    };

    const res = await fetch(
        "/entry/",
        {
            method : "POST",
            headers : {"Content-Type" : "application/json"},
            body : JSON.stringify(querys)
        }
    );

    //入力エラー
    if(res.status == 422){
        window.location.href = "/entry/?result=登録失敗";
    }
    //正常入力
    else{
        const result = await res.json();
        window.location.href = "/entry/?result=" + result.entry_result;
    }
}

//エントリー終了
const exitEntry = async() => {

    //DB(=ランニング記録)の更新はこのタイミングで行う
    const result = await fetch(
        "/updateDB/",
        {
            method : "POST",
            headers : {"content-Type" : "application/json"}
        }
    );

    const items = await result.json();
    const status = items.entry_exit_result;
    if(status == 'NoData'){
        //DBの登録データが0の場合、app_entry画面に戻る
        window.location.href = "/entry/?result=" + 'ランニング記録を1件以上登録してください';
    }
    else{
        //推論画面(app_inference)に遷移
        window.location.href = "/inference/";
    }
}
