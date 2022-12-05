let net = null;



function showFiles() {
  // An empty img element
  let demoImage = document.getElementById('idImage');
  // read the file from the user
  let file = document.querySelector('input[type=file]').files[0];
  const reader = new FileReader();
  reader.onload = function (event) {
    demoImage.src = reader.result;
  }
  reader.readAsDataURL(file);
  app();
}

async function app() {
  console.log('loading mobilenet...');
  net = await mobilenet.load();
  console.log('Sucessfully loaded model');
  await predice();
}

async function predice() {
  img_ = document.getElementById('idImage');
  file = document.querySelector('input[type=file]').files[0];
  console.log("predice()");


  if (img_.src != "") {
    var formData = new FormData();
    let file = document.querySelector('input[type=file]').files[0];
    formData.append("image", file);

    var request = new XMLHttpRequest();
    request.open("POST", "http://127.0.0.1:8080/api/task", false);
    request.send(formData);
    result = request.response
    console.log(result);
    predict_res = JSON.parse(result)["data"]["result"]
    document.getElementById('predict').innerHTML = predict_res;
  }

  //   var fd = new FormData();
  //   fd.append('image', img_ /*, optional filename */)

  //   var req = jQuery.ajax({
  //     url: 'api/task', 
  //     method: 'POST',
  //     data: fd, // sends fields with filename mimetype etc
  //     // data: aFiles[0], // optional just sends the binary
  //     processData: false, // don't let jquery process the data
  //     contentType: false // let xhr set the content type
  //   });

  //   // jQuery is promise A++ compatible and is the todays norms of doing things 
  //   req.then(function(response) {
  //     console.log(response);
  //     // drawStacked(response);
  //   }, function(xhr) {
  //     console.error('failed to fetch xhr', xhr)
  //   })
  //   drawStacked(result);
  //   console.log(result);
  // }
}

app();