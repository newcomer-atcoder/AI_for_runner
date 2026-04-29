//実際に走る距離(km)」の推論
const inference_your_distance = async() => {
    distance = document.getElementById("distance").value;
    condition = document.getElementById("condition").value;

    const res = await fetch(
        "/inference/?distance=" + distance + "&condition=" + condition,
        {
            method : "POST",
            headers : {"Content-Type" : "application/json"},
        }
    );

    //入力エラー
    if(res.status == 422){
        window.location.href = "/inference/?result=入力エラー";
    }
    //正常入力
    else{
        const result = await res.json();
        window.location.href = "/inference/?result=" + result.inference_result;
    }
}

//推論結果を、次の走行予定として保存する機能
const saveAsSchedule = async() => {
    //保存機能を呼び出す
    const saveInfo = document.querySelector('.message-area input[type="text"]').value;
    const res = await fetch(
        "/save/?saveInfo=" + saveInfo,
        {
            method : "POST",
        }
    );

    //推論画面に戻る
    const item = await res.json();
    const result = item.result;
    window.location.href = "/inference/?result=" + result;
}