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