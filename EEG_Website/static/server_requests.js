/*
 Fetch selected electrode data
 */
function displayData(delta=0) {
    const query = '/data?delta=' + delta.toString();
    console.log(query);
    fetch(query)
            .then(response => response.json())
            .then(json => {
                let id;
                const graphs = document.getElementById('time_series');
                while (graphs.firstChild) {
                    graphs.removeChild(graphs.firstChild);
                }
                const graph_height = 560 / Object.keys(json.data).length;
                let count = 1;
                const total = Object.keys(json.data).length;
                for (id in Object.keys(json.data)) {
                    graphs.appendChild(createChartElementFrom(json, id, count, total, graph_height));
                    count++;
                }
            });
}


/*
 Toggle select electrode form
 Fetch electrode labels
 Dynamically add check inputs to electrode form for each electrode
 */
function openElectrodeSelect() {
    const electrodeForm = document.getElementById('electrode_form');
    electrodeForm.style.display = (electrodeForm.style.display === 'none') ? 'block' : 'none';
    fetch('/electrode_get')
            .then(response => response.json())
            .then(json => {
                //Delete all checkboxes except for label in form
                while (electrodeForm.firstChild) {
                    electrodeForm.removeChild(electrodeForm.firstChild);
                }
                Object.keys(json.values).forEach( id=> {
                    electrodeForm.appendChild(getElectrodeSelectElement(id,json.values[id].trim()))
                });
                const submit = document.createElement('input');
                submit.setAttribute('type', 'submit');
                submit.setAttribute('onClick', 'openElectrodeSelect();')
                electrodeForm.appendChild(submit);
                electrodeForm.appendChild(document.createElement('br'));
                saveElectrodeSelect();
            });
}


//save the state of the checkboxes
function saveElectrodeSelect() {
    fetch('/electrode_select')
        .then(response => response.json())
        .then(json=> {
            var val;
            console.log(json);

            for (val in json.data) {
                let str = json.data[val].toString().trim();
                console.log(str);
                document.getElementById(str).checked = true;
                }
        })
}


/*
  Display annotations
 */
function toggleAnnotate() {
    const query = '/ann_data';
    fetch(query).then(response => response.json()).then(json => {
        const amplitude = parseInt(json.amplitude);
        console.log(json);
        charts.forEach(chart => {
            if (!('annotations' in chart.options.annotation)) {
                console.log("displaying..." + json.amplitude);

                let index;
                let anns = [];
                for (index in json.annotations) {
                    const annotation_config = {
                        type: 'box',
                        mode: 'vertical',
                        xScaleID: 'x-axis-0',
                        yScaleID: 'y-axis-0',
                        scaleID: 'x-axis-0',
                        // Left edge of the box. in units along the x axis
                        xMin: json.annotations[index]['start'],
                        xMax: json.annotations[index]['end'],
                        yMax: amplitude,
                        yMin: -1 * amplitude,
                        content: "Test label",
                        borderColor: 'grey',
                        borderWidth: 0,
                    }
                    anns.push(annotation_config);
                }
                console.log(anns);
                chart.options.annotation =
                    {
                        annotations: anns
                    }
            }
            else {
                delete chart.options.annotation['annotations'];
            }
            chart.update();
        });
    });
}


/*
  Change amplitude by 100 up/down
 */
function alterAmplitudes(delta) {
    const query = '/amplitude?delta=' + delta.toString();
    fetch(query).then(response => response.json()).then(json => {
        const amplitude = parseInt(json.amplitude);
        charts.forEach(chart => {
            chart.options.scales.yAxes[0].ticks.max = amplitude;
            chart.options.scales.yAxes[0].ticks.min = -1 * amplitude;
            chart.options.scales.yAxes[0].ticks.stepSize = amplitude;
            chart.update()
        });
    });
}
