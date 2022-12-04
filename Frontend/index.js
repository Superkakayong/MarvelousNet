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

google.charts.load('current', { packages: ['corechart', 'bar'] });

function drawStacked(result) {
  var data_ = Array((result.length + 1));
  data_[0] = ['clase', 'Probabilidad', { role: "style" }];
  data_[1] = [result[0].className, result[0].probability, '#982107'];
  for (iter = 1; iter < result.length; iter++) {
    data_[(iter + 1)] = [result[iter].className, result[iter].probability, '#6F76C2'];
  }
  var data = google.visualization.arrayToDataTable(data_);
  var view = new google.visualization.DataView(data);
  view.setColumns([0, 1,
    {
      calc: "stringify",
      sourceColumn: 1,
      type: "string",
      role: "annotation"
    },
    2]);
  var options = {
    width: 600,
    height: 200,
    bar: { groupWidth: "95%" },
    legend: { position: "none" },
  };
  var chart = new google.visualization.BarChart(document.getElementById('chart_div'));
  chart.draw(view, options);
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
    let yourUrl = "http://127.0.0.1:8080/api/task";
    fetch(yourUrl, {
      method: 'POST',
      headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
      },
      body: JSON.stringify({ "id": 78912 })
    })
    .then(response => response.json())
    .then(response => console.log(JSON.stringify(response)))
    // var fd = new FormData();
    // fd.append('image', img_ /*, optional filename */)

    // var req = jQuery.ajax({
    //   url: 'api/task', 
    //   method: 'POST',
    //   data: fd, // sends fields with filename mimetype etc
    //   // data: aFiles[0], // optional just sends the binary
    //   processData: false, // don't let jquery process the data
    //   contentType: false // let xhr set the content type
    // });

    // // jQuery is promise A++ compatible and is the todays norms of doing things 
    // req.then(function(response) {
    //   console.log(response);
    //   // drawStacked(response);
    // }, function(xhr) {
    //   console.error('failed to fetch xhr', xhr)
    // })
    // drawStacked(result);
    // console.log(result);
  }
}

app();