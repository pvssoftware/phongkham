

$(function(){
    endpoint = 'ws://127.0.0.1:8000/list-patients/' // 1

    var socket =  new ReconnectingWebSocket(endpoint) // 2
    
   // 3
    socket.onopen = function(e){
      console.log("open", e); 
    }
    socket.onmessage = function(e){
      console.log("message", e);
      var patientData = JSON.parse(e.data);
      $("#list_patients").html(patientData.html_patients);
    }
    socket.onerror = function(e){
      console.log("error", e)
    }
    socket.onclose = function(e){
      console.log("close", e)
    }
});