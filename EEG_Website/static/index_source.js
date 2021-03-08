/*
 Function that runs on load, calling other functions as designated by url parameters
 */
function loadIndexPage() {
    const queryString = window.location.search;
    let urlParams = new URLSearchParams(queryString);
    if (urlParams.has("electrodes")) {
        openElectrodeSelect();
    }
    if (urlParams.has("display")) {
        displayData(0);
    }
}

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
            })

}

function createChartElementFrom(json, id, count, total, height) {
    const name = Object.keys(json.data)[id];
    console.log(name);
    let data_map = {};
    data_map['label'] = name;
    data_map['data'] = json.data[name].map(Number);
    data_map['pointRadius'] = 0;
    data_map['fill'] = false;
    if (count % 2 === 1) {
        data_map['borderColor'] = '#880808';
    }



    let canvasElem = document.createElement('canvas');

    canvasElem.setAttribute('height', height.toString());
    canvasElem.setAttribute('width', '900');
    canvasElem.setAttribute('id', [name,'chart'].join(''));

    let chart = new Chart(canvasElem.getContext('2d'), {
                    type: 'line',
                    data: {
                        labels: json.time,
                        datasets: [data_map],
                    },
                    options: {
                            scales: {
                                xAxes: [{
                                    display: (count === total),
                                    gridLines: {
                                        drawOnChartArea: false
                                    }
                                }],
                                yAxes: [{
                                     ticks: {
                                max: 200,
                                min: -200,
                                stepSize: 200,
                                maxTicksLimit: 3
                            },
                                    gridLines: {
                                        drawOnChartArea: false
                                    }
                                }]
                            },
                            legend: {
                                display: true,
                                position: 'left',
                                align: 'end'
                            }
                        }
                });
    return canvasElem;
}



/*
 Toggle select file form
 */
function openFileSelect() {
    const fileForm = document.getElementById('file_form');
    fileForm.style.display = (fileForm.style.display === 'none') ? 'block' : 'none';
}

/*
 Toggle duration select
 */
function openDurationSelect() {
    const fileForm = document.getElementById('duration_form');
    fileForm.style.display = (fileForm.style.display === 'none') ? 'block' : 'none';
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
                console.log(JSON.stringify(json))
                //Delete all checkboxes except for label in form
                while (electrodeForm.firstChild) {
                    electrodeForm.removeChild(electrodeForm.firstChild);
                }
                const label = document.createElement('label');
                label.innerText = 'Select Electrodes';
                label.setAttribute('for', 'electrode_form');
                electrodeForm.appendChild(label);
                electrodeForm.appendChild(document.createElement('br'));
                Object.keys(json.values).forEach( id=> {
                    electrodeForm.appendChild(getElectrodeSelectElement(id,json.values[id]))
                });
                const submit = document.createElement('input');
                submit.setAttribute('type', 'submit');
                submit.setAttribute('onClick', 'openElectrodeSelect();')
                electrodeForm.appendChild(submit);
            });
}


/*
 Create HTML element for electrode
 */
function getElectrodeSelectElement(id, value) {
    const elem = document.createElement('span');
    const elemLabel = document.createElement('label');
    elemLabel.textContent = value;
    elemLabel.setAttribute('for', value )
    const elemCheckBox = document.createElement('input');
    elemCheckBox.setAttribute('type', 'checkbox');
    elemCheckBox.setAttribute('value', id);
    elemCheckBox.setAttribute('id', value);
    elemCheckBox.setAttribute('name', value);
    elem.appendChild(elemCheckBox);
    elem.appendChild(elemLabel);
    elem.appendChild(document.createElement('br'));

    return elem;
}
