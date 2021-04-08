let chart = null;
let dataSet = null;

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
    $('.annotation-item').fadeOut();
    $('.annotation-menu').fadeOut();
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
    //labelsList();

}

function labelsList() {
    console.log("Got called");
        fetch('/ann_data?byTime=false')
            .then(response => response.json())
            .then(json => {
                /*List all the names of labels */
                const elem = document.getElementById('ann_list');
                var val;
                for (i in json.annotations) {
                    const label = json.annotations[i]["Annotation"];
                    const offset = json.annotations[i]["Onset"];
                    let li = document.createElement("li");
                    let link = document.createElement("a");
                    link.value = offset;
                    let text = document.createTextNode(label);
                    link.appendChild(text);
                    link.style.cursor = "pointer";
                    link.onclick = function () {
                        $.post('/select-offset', {new_value: this.value},
                        function (response) {
                            displayData(0);
                        });
                    };
                    li.appendChild(link);
                    elem.appendChild(li);

                }
            });

}
/*
    CREATE ELEMENTS
 */
function createDataObject(data, id) {
    const name = id;
    let data_map = {};
    data_map['label'] = name.trimEnd();
    data_map['data'] = data.map(Number);
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
    dataSet = data_map;
    chart = new Chart(canvasElem.getContext('2d'), {
                    type: 'line',
                    data: {
                        labels: time,
                        datasets: data_map,
                    },
                    options: {
                        scales: {
                            max: data_map.length * dataOffset,
                            min: -1 * dataOffset,
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
                                    stepSize: dataOffset,
                                    callback: function (value, index, values) {
                                        const dataIndex = dataSet.length - index;
                                        if (dataIndex >= 0 && index > 0) {
                                            return dataSet[dataIndex].label;
                                        } else {
                                            return '';
                                        }
                                    }
                                },
                                gridLines: {
                                    drawOnChartArea: false
                                }
                            }]
                        },
                        legend: {
                            display: false,
                        },
                        annotation: {},
                        layout: {
                            padding: {
                                left: 50
                            }
                        },
                        events: []
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

//Create annotation element
function createAnnotationElementFrom(label, start, end, max, min) {
    let annotation = $('<a>', {class:'annotation-item', id:label});
    annotation.text(label);
    annotation.val(start)
    annotation.click( function () {
        const annotation_offset  = this.value;
        console.log(annotation_offset);
        $.post('/select-offset', {new_value: annotation_offset},
            function () {
            displayData(0);
        });
    });

    return annotation;
}
/*
    ALTER CHARTS
 */
function changeData(data_maps, time) {
    chart.data.labels = time;
    chart.data.datasets = data_maps;
    chart.update(0);
}








