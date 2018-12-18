function rewriteFormModal(week,time){
    let weeks = ["月","火","水","木","金"]
    document.getElementById("form-week").innerText = "曜日　："+weeks[week]+"曜日";
    document.getElementById("form-time").innerText = "時間　："+String(time)+"時限";
}
