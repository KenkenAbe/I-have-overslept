function rewriteFormModal(week,time){
    let weeks = ["月","火","水","木","金","土"];
    document.getElementById("form-week").value = weeks[week];
    document.getElementById("form-time").value = String(time);
    var user_cookie = getCookieArray()["key"];
    if (user_cookie.slice(0,1) == "\""){
      user_cookie = user_cookie.slice(1)
    }
    connectAPI(user_cookie,week,time).done(function(response){
        //通信が正常終了した場合の処理
        if(response.status == 'accepted'){
        document.getElementsByName("title")[0].value = response.content[0].fields.title;
        document.getElementsByName("teacher")[0].value = response.content[0].fields.teacher;
        document.getElementsByName("room")[0].value = response.content[0].fields.room;
        document.getElementsByName("quater")[0].value = response.content[0].fields.quater;
        document.getElementsByName("week")[0].value = response.content[0].fields.week;
        document.getElementsByName("time")[0].value = response.content[0].fields.time;}
        //この先、responseの中に仕様の通りデータが入っているのでこれを使ってフォームを埋めてほしいです・・・
        console.log(response);
        if (response.status == "accepted"){
            document.getElementsByName("teacher")[0].value = response.content[0].fields.teacher;
            document.getElementsByName("title")[0].value = response.content[0].fields.title;
            document.getElementsByName("room")[0].value = response.content[0].fields.room;
            document.getElementsByName("quater")[0].value = response.content[0].fields.quater;
        }else{
            document.getElementsByName("teacher")[0].value = "";
            document.getElementsByName("title")[0].value = "";
            document.getElementsByName("room")[0].value = "";
            document.getElementsByName("quater")[0].value = "";
        }
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

function connectAPI(token,week,time){
    return $.ajax({
        url: "https://scheduler.iniadstulab.jp/api/v1/schedules/json?week="+week+"&time="+time,
        dataType: "json",
        type: "GET",
        beforeSend: function(xhr){
            xhr.setRequestHeader("Authorization",token);
        }
    })
}