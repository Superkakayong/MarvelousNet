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
  console.log("predice()");
  if (img_.src != "") {
    var formData = new FormData();
    let file = document.querySelector('input[type=file]').files[0];
    formData.append("image", file);

    var request = new XMLHttpRequest();
    request.open("POST", "api/task", false);
    request.send(formData);
    result = request.response
    console.log(result);
    predict_res = JSON.parse(result)["data"]["result"]
    document.getElementById('predict').innerHTML = predict_res;
  }
}

app();