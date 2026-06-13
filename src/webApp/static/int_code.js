async function deleteRecord(id){
    await fetch(
        '/api/delete/',
        {
            method: "DELETE",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({id: id})
        }
    );
}