function rewriteFormModal(week,time){
    let weeks = ["月","火","水","木","金","土"];
    document.getElementById("form-week").value = weeks[week];
    document.getElementById("form-time").value = String(time);
    var user_cookie = getCookieArray()["key"];
    connectAPI(user_cookie).done(function(response){
        //通信が正常終了した場合の処理
        //この先、responseの中に仕様の通りデータが入っているのでこれを使ってフォームを埋めてほしいです・・・
        console.log(response);
    }).fail(function(error){
        //通信が異常終了した場合の処理
        console.log(error);
    })
}

function getCookieArray(){
  var arr = new Array();
  if(document.cookie != ''){
    var tmp = document.cookie.split('; ');
    for(var i=0;i<tmp.length;i++){
      var data = tmp[i].split('=');
      arr[data[0]] = decodeURIComponent(data[1]);
    }
  }
  return arr;
}

function connectAPI(token){
    return $.ajax({
        url: "https://scheduler.iniadstulab.jp/api/v1/schedules/json",
        dataType: "json",
        type: "GET",
        beforeSend: function(xhr){
            xhr.setRequestHeader("Authorization",token);
        }
    })
}