//アプリの最初の画面(=app_init.html)から
//ランニング記録エントリー画面 or AI推論画面のどちらかに遷移
const goto_nextPage = () => {
    //遷移する画面を決定
    const entry = document.querySelector('.radio-group input[type="radio"]:checked');
    const next_url = (entry.value == "y")? "/entry/" : "/inference/"

    //リダイレクト
    window.location.href = next_url;
}

