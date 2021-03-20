charts = []

/*
    CONFIGURE PAGE ON LOAD
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
    if (urlParams.has("filename")) {
        const title = document.createElement('h3')
        title.innerText = urlParams.get('filename');
        document.getElementById('title').appendChild(title);

    }
    if (urlParams.has("annotations")) {
        displayData(0);
    }
    document.getElementById('body').addEventListener('keydown', function(event) {
        const key = event.code;
        if (key === "ArrowLeft") {
            displayData(-1);
        }
        else if (key === "ArrowRight") {
            displayData(1);
        }
    } );

}


/*
    TOGGLE PAGE ELEMNTS
 */
// Toggle select file form
function openFileSelect() {
    const fileForm = document.getElementById('file_form');
    fileForm.style.display = (fileForm.style.display === 'none') ? 'block' : 'none';
}

// Toggle duration select
function openDurationSelect() {
    const fileForm = document.getElementById('duration_form');
    fileForm.style.display = (fileForm.style.display === 'none') ? 'block' : 'none';
}

// Toggle select annotation form
function openAnnotationSelect() {
    const annotationForm = document.getElementById('ann_file_form');
    annotationForm.style.display = (annotationForm.style.display === 'none') ? 'block' : 'none';
}

/*
    CREATE ELEMENTS
 */
//Build single time series chart
function createChartElementFrom(json, id, count, total, height) {
    const name = Object.keys(json.data)[id];
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
                            x: {
                                type: 'timeseries'
                            },
                            xAxes: [{
                                display: (count === total),
                                gridLines: {
                                    drawOnChartArea: false
                                },
                                ticks: {
                                    maxTicksLimit: 2
                                }
                            }],
                            yAxes: [{
                                ticks: {
                                    max: parseInt(json.amplitude),
                                    min: -1 * parseInt(json.amplitude),
                                    stepSize: parseInt(json.amplitude),
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
                            align: 'center',
                            usePointStyle: true,
                            rotation: 90
                        },
                        annotation: {

                        }

                    }
                });
    charts.push(chart);

    document.getElementById('body').addEventListener('keydown', function(event) {
        const key = event.code;
        if (key === "ArrowUp") { alterAmplitudes(100);}
        else if (key === "ArrowDown") { alterAmplitudes(-100); }
    });
    return canvasElem;
}

// Create HTML element for electrode
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









