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
    var formData = new FormData();
    let file = document.querySelector('input[type=file]').files[0];
    formData.append("image", file);

    var content = '<a id="a"><b id="b">hey!</b></a>'; // 新文件的正文
    var blob = new Blob([content], { type: "text/xml" });
    formData.append("webmasterfile", blob);

    var request = new XMLHttpRequest();
    request.open("POST", "http://127.0.0.1:8080/api/task", false);
    request.send(formData);
    console.log(request.response);

    // var response = new XMLHttpRequest();
    // response.onreadystatechange = () => {
    //   if (response.readyState === 4) {
    //     callback(response.response);
    //     console.log(response.response);
    //   }
    // }

    // response.open('GET', "http://127.0.0.1:8080/api/task", true);
    // console.log(response.response);
    // response.send('');

    // xhr.send(formData);

    //   if (xhr.status != 200) {
    //     console.log(`Error ${xhr.status}: ${xhr.statusText}`);
    //   } else {
    //     console.log(xhr.response);
    //   }


    // let yourUrl = "http://127.0.0.1:8080/api/task";
    // fetch(yourUrl, {
    //   method: 'POST',
    //   headers: {
    //       'Accept': 'application/json',
    //       'Content-Type': 'application/json'
    //   },
    //   body: JSON.stringify({ "id": 78912 })
    // })
    // .then(response => response.json())
    // .then(response => console.log(JSON.stringify(response)))

    // drawStacked(result);
    // console.log(result);
  }
}

app();