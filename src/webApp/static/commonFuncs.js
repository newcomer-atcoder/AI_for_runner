//404 Not Foundの時にアプリを再起動する(=最初の画面に戻る)
const reloadApp = () => {
    window.location.href = "/";
}

//アプリ本体を終了
const exitApp = async() => {
    await fetch(
        "/exit/",
        {
            method : "POST",
            headers : {"ContentType" : "application/json"}
        }
    )
}