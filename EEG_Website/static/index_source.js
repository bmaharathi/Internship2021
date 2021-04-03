let chart = null;

/*
    CONFIGURE PAGE ON LOAD
 */
function loadIndexPage() {
    const queryString = window.location.search;
    let urlParams = new URLSearchParams(queryString);
    setSlider();
    if (urlParams.has("electrodes")) {
        openElectrodeSelect();
    }
    if (urlParams.has("display")) {
        displayData(0);
        // removeUnselected();
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
        event.preventDefault();
        const key = event.code;
        if (key === "ArrowLeft") {
            displayData(-1);
        }
        else if (key === "ArrowRight") {
            displayData(1);
        }
    });
    $('#sidebarItems').fadeOut();
    $('#sidebarMenu').animate({'width' : '3%'});
    $('#sidebarMenu').mouseenter(function () {
        $('#sidebarMenu').animate({'width' : '13%'});
        $('#sidebarItems').fadeIn();

    });
    $('#sidebarMenu').mouseleave(function () {
        $('#sidebarItems').fadeOut();
        $('#sidebarMenu').animate({'width' : '3%'});
    })

}


/*
    TOGGLE PAGE ELEMNTS
 */
// Toggle select file form
function openFileSelect() {
    $('#eeg_file').change(function () {
        $.post('/upload_eeg', {eeg_file: this.value}, function() {
            displayData(0);
        });
    });
    $('#eeg_file').click();
}

// Toggle duration select
function openDurationSelect() {
    $('#duration_form').slideToggle();
    // const fileForm = document.getElementById('duration_form');
    // fileForm.style.display = (fileForm.style.display === 'none') ? 'block' : 'none';
}

// Toggle select annotation form
function openAnnotationSelect() {
    $('#ann_file').change(function () {
        $.post('/upload_ann', {ann_file: this.value});
    });
    $('#ann_file').click();
}

/*
    CREATE ELEMENTS
 */
function createDataObject(json, id) {
    const name = Object.keys(json.data)[id];
    let data_map = {};
    data_map['label'] = name.trimEnd();
    data_map['data'] = json.data[name].map(Number);
    data_map['pointRadius'] = 0;
    data_map['fill'] = false;

    return data_map;
}

//Build single time series chart
function createChartElementFrom(time, data_map, dataOffset) {
    let canvasElem = document.createElement('canvas');
    console.log(dataOffset);

    canvasElem.setAttribute('height', '40%');
    canvasElem.setAttribute('width', '80%');
    canvasElem.setAttribute('id', 'main-chart');
    canvasElem.style.zIndex = -1;
    chart = new Chart(canvasElem.getContext('2d'), {
                    type: 'line',
                    data: {
                        labels: time,
                        datasets: data_map,
                    },
                    options: {
                        scales: {
                            x: {
                                type: 'timeseries'
                            },
                            xAxes: [{
                                display: true,
                                gridLines: {
                                    drawOnChartArea: false
                                },
                                ticks: {
                                    maxTicksLimit: 2,
                                    maxRotation: 0,
                                    minRotation: 0
                                }
                            }],
                            yAxes: [{
                                ticks: {
                                    display : false,
                                    max: data_map.length * dataOffset,
                                    min: -1 * dataOffset
                                },
                                gridLines: {
                                    drawOnChartArea: false
                                }
                            }]
                        },
                        legend: {
                            display: false,
                        },
                        annotation: {

                        },
                        layout: {
                            padding: {
                                left: 50
                            }
                        }
                    }
                });

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

/*
    ALTER CHARTS
 */
function changeData(data_maps, time) {
    chart.data.labels = time;
    chart.data.datasets = data_maps;
    chart.update(0);
}








