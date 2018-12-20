function rewriteFormModal(week,time){
    let weeks = ["月","火","水","木","金"]
    document.getElementById("form-week").value = weeks[week];
    document.getElementById("form-time").value = String(time);
}
