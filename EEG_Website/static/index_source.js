let chart = null;
let dataSet = null;

/*
    CONFIGURE PAGE ON LOAD
 */
function loadIndexPage() {
    // Create url object to check status of current workflow
    const queryString = window.location.search;
    $('.slidecontainer').hide();
    let urlParams = new URLSearchParams(queryString);
    // Select electrodes
    if (urlParams.has("electrodes")) {
        openElectrodeSelect();
    }
    // Display time series graph
    if (urlParams.has("display")) {
        displayData(0);
    }
    // Display current file name
    if (urlParams.has("filename")) {
        const title = document.createElement('h3')
        title.innerText = urlParams.get('filename');
        document.getElementById('title').appendChild(title);
    }
    // ???????
    if (urlParams.has("annotations")) {
        displayData(0);
    }
    // Set up event listeners to step through data using arrow keys
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
    // Set up left side bar
    // TODO: FIX HOVER TO AVOID CLOSING EARLY
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
    // Hide annotation menu
    // TODO: FIX STYLING
    $('#annotation-items').hide();
    $('.annotation-menu').animate({'width': '0%', 'left': '100%'});
    setSlider();
}


/*
    TOGGLE PAGE ELEMNTS
 */
// Toggle select file form
function openFileSelect() {
    // add event listener to post name of file then display data
    $('#eeg_file').change(function () {
        $.post('/upload_eeg', {eeg_file: this.value}, function() {
            displayData(0);
        });
    });
    // Opens up select file prompt
    $('#eeg_file').click();
}

// Toggle duration select
function openDurationSelect() {
    $('#duration_form').slideToggle();
}

// Toggle select annotation form
function openAnnotationSelect() {
    $('#ann_file').change(function () {
        $.post('/upload_ann', {ann_file: this.value});
    });
    $('#ann_file').click();
}


// open annotations menu and get annotations to list
function listAnnotations() {
    $('#annotation-items').empty();
    getAnnotationsToList();
    // TODO: FIX ANIMATION
    $('#annotation-items').show();
    $('.annotation-menu').animate({'width': '50%', 'left': '85%'});
}

/*
    CREATE ELEMENTS
 */
// Create single channel configuration for chart js
function createDataObject(data, id) {
    const name = id;
    let data_map = {};
    data_map['label'] = name.trimEnd();
    data_map['data'] = data.map(Number);
    data_map['pointRadius'] = 0;
    data_map['fill'] = false;
    data_map['borderColor'] = '#51A1E8';
    data_map['borderWidth'] = 2;
    return data_map;
}

//Build single time series chart
function createChartElementFrom(time, data_map, dataOffset) {
    // HTML Canvas element
    let canvasElem = document.createElement('canvas');
    canvasElem.setAttribute('id', 'main-chart');
    // TODO: MOVE STYLING TO CSS FILE
    canvasElem.setAttribute('height', '40%');
    canvasElem.setAttribute('width', '80%');
    canvasElem.style.zIndex = -1;
    dataSet = data_map;
    //Display actual chart
    chart = new Chart(canvasElem.getContext('2d'), {
                    type: 'line',
                    data: {
                        labels: time,
                        datasets: data_map,
                    },
                    options: {
                        scales: {
                            // Data limits (change to maintain orderly display of channels)
                            max: data_map.length * dataOffset,
                            min: -1 * dataOffset,
                            // Label type (hours)
                            x: {
                                type: 'timeseries'
                            },
                            // X axes label (display only beginning and end time of current view)
                            // TODO: CHANGE FONTS
                            xAxes: [{
                                display: true,
                                gridLines: {
                                    drawOnChartArea: false,
                                    drawOnChartArea: true,
                                    drawTicks: false
                                },
                                ticks: {
                                    padding: 15,
                                    maxTicksLimit: time.length / 1000,
                                    stepSize: 1000,
                                    maxRotation: 0,
                                    minRotation: 0,
                                    fontWeight: 'bold',
                                    fontSize: 15,
                                    callback: function (value, index, values) {
                                        const timevalues = value.split(':')
                                        let timelabel = new Date();
                                        timelabel.setHours(parseInt(timevalues[0]), parseInt(timevalues[1]), parseInt(timevalues[2]));
                                        if (index == 0 || index == time.length - 1) {
                                            if (index == 0) {
                                                $('#sliderdisplay').text(timelabel.toLocaleTimeString());
                                            }
                                            return timelabel.toLocaleTimeString();
                                        } else {
                                            return '';
                                        }
                                    }
                                }
                            }],
                            // Y axis labels (used to display channel names
                            yAxes: [{
                                //TODO: FIX ALIGNMENT WHICH BREAKS ON AMPLITUDE CHANGES
                                ticks: {
                                    // Step size used to align channel name with graph
                                    stepSize: dataOffset,
                                    // Change label from numerical value to the name of the channel at tick offset
                                    callback: function (value, index, values) {
                                        const dataIndex = dataSet.length - index;
                                        if (dataIndex >= 0 && index > 0) {
                                            return dataSet[dataIndex].label;
                                        } else {
                                            return '';
                                        }
                                    },
                                    fontWeight: 'bold',
                                    fontSize: 14
                                },
                                // TODO: DISPLAY DASHED GRIDLINES DEPENDENDT ON DURATION VIEWED
                                gridLines: {
                                    drawOnChartArea: false
                                }
                            }]
                        },
                        // Prevent legend display because it doesn't optimize space or align with channels
                        legend: {
                            display: false,
                            label: {
                                font: {
                                    weight: 'bold',
                                    size: 50
                                }
                            }
                        },
                        // Annotation section (filled in when displaying annotations
                        annotation: {},
                        // Padding of graph
                        layout: {
                            padding: {
                                left: 50
                            }
                        },
                        // Erases default events
                        //TODO: ADD CALLBACK TO CHANGE CHANNEL COLOR
                        events: []
                    }
                });

    // Adds event listener to change amplitude based on up/down arrow keys
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
function createAnnotationElementFrom(label, start, end) {
    //create html elements
    let li = document.createElement("li");
    let link = document.createElement("a");
    // set value of link to starr offset
    link.value = start;
    // Adds annotation label to element
    let text = document.createTextNode(label);
    link.appendChild(text);
    // Changes cursor to the pointer when hovering over annotation
    link.style.cursor = "pointer";
    // Go to annotation when clicked then display annotation
    link.onclick = function () {
        const argument = "&chosen=" + label;
        $.post('/select-offset', {new_value: this.value},
        function (response) {
            displayData(0);
            toggleAnnotate(argument, label);
            $('#annotation-items').hide();
            $('.annotation-menu').animate({'width': '0%', 'left': '100%'});
        });
    };

    li.appendChild(link);
    return li;
}


/*
    ALTER CHARTS
 */
function changeData(data_maps, time) {
    chart.data.labels = time;
    chart.data.datasets = data_maps;
    chart.update(0);
}








