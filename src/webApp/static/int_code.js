async function deleteRecord(id){
    await fetch(
        '/api/delete/',
        {
            method: "DELETE",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({id: id})
        }
    );

    window.location.href = '/';
}

async function updPage(nextFlg, page){
    console.log(Number(page))
    const nextPage = Number(page) + (nextFlg? 1: -1);
    await fetch(
        `/api/updPage/?page=` + String(nextPage),
        {
            method: 'GET' //念の為明示的に指定する
        }
    );

    window.location.href = '/?page=' + nextPage;
}