// Global object which will indicate the start of data recording for use with timeslider
let startTime = new Date();

/*
 Fetch selected electrode data
 */
function displayData(delta=0) {
    // Display data at currentoffset + delta
    const query = '/data?delta=' + delta.toString();
    fetch(query)
            .then(response => response.json())
            .then(json => {
                // Create object to hold chart js configurations for each channel
                let data_maps = [];
                for (let id in json.data) {
                    data_maps.push(createDataObject(json.data[id][1], json.data[id][0]));
                }
                // If no existing chart create new chart
                const graphs = document.getElementById('time_series');
                if (!graphs.hasChildNodes()) {
                    $('#time_series').append(createChartElementFrom(json.time, data_maps, parseInt(json.dataOffset)));
                }
                // else update current chart with new configurations and time labels
                else {
                    changeData(data_maps, json.time)
                }
                // update slider
                setSlider();
                // Update duration display
                $('#duration').val(parseInt(json.duration));
            });
}



/*
 Toggle select electrode form
 Fetch electrode labels
 Dynamically add check inputs to electrode form for each electrode
 */
function openElectrodeSelect() {
    $('#electrode_form').slideToggle();
    fetch('/electrode_get')
            .then(response => response.json())
            .then(json => {
                //Delete all checkboxes except for label in form
                $('#electrode_form').empty();
                Object.keys(json.values).forEach( id=> {
                    $('#electrode_form').append(getElectrodeSelectElement(id,json.values[id].trim()))
                });
                // Add submit button
                const submit = document.createElement('input');
                submit.setAttribute('type', 'submit');
                submit.setAttribute('onClick', 'openElectrodeSelect();')
                $('#electrode_form').append(submit);
                $('#electrode_form').append(document.createElement('br'));
                //Check off selected values
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
  Annotations
 */
// TODO: TEST
//Display annotations on chart
function toggleAnnotate(selectArg="", chosenName="") {
    const query = '/ann_data?byTime=true' + selectArg;
    fetch(query).then(response => response.json()).then(json => {
        // if (!('annotations' in chart.options.annotation)) {
            let anns = [];
            for (let index in json.annotations) {
                // Parse annotation attributes
                const start = json.annotations[index]['start'];
                const end = json.annotations[index]['end'];
                const max = parseInt(json.annotations['chart_max']);
                const min = parseInt(json.annotations['chart_min']);
                const label = json.annotations[index]['label'];

                const color = (label === chosenName) ? 'yellow' : 'grey'
                // Create chart js configuration for annotation with chosen annotations highlighted
                const annotation_config = {
                    type: 'box',
                    mode: 'vertical',
                    xScaleID: 'x-axis-0',
                    yScaleID: 'y-axis-0',
                    scaleID: 'x-axis-0',
                    // Left edge of the box. in units along the x axis
                    xMin: start,
                    xMax: end,
                    yMax: max,
                    yMin: min,
                    content: "Test label",
                    borderColor: color,
                    borderWidth: 1,
                }
                // Append configuration to list of configurations
                anns.push(annotation_config);
            }
            //Adds annotations and to chartjs object and update
            chart.options.annotation = {annotations: anns};
        // } else {
        //     delete chart.options.annotation['annotations'];
        // }
        chart.update();
    });
}

// List annotation in right side bar
function getAnnotationsToList() {
    const query = '/ann_data?byTime=false';
    fetch(query).then(response => response.json()).then(json => {
        for (let index in json.annotations) {
            // Calculate offset to jump to when selected (currently .3 of selected duration ahead of annotation onset to the nearest second)
            const onset = parseInt(json.annotations[index]['Onset']);
            const duration = parseInt(json.duration) * 1000;
            let start = onset - Math.floor(.3 * duration)
            start = start - start % 1000;
            start = (start > 0) ? start : 0;

            const label = json.annotations[index]['Annotation'];
            // create and append annotation item to right sider bar
            $('#annotation-items').append(createAnnotationElementFrom(label, start));
        }
        chart.update();
    });
}


/*
  Change amplitude by 100 up/down
 */
// TODO: FIND OUT WHERE CHANNEL LABELING BREAKS (possible change in tick size)
function alterAmplitudes(delta) {
    const query = '/amplitude?delta=' + delta.toString();
    fetch(query).then(response => response.json()).then( json => {
        const amplitude = parseInt(json.amplitude);
        const newMax = parseInt(json.newMax);
        const newMin = parseInt(json.newMin);
        chart.options.scales.max = newMax;
        chart.options.scales.min = newMin;
        chart.options.scales.yAxes[0].ticks.stepSize = amplitude;
        chart.update(0)
        displayData(0);
    });
}

/*
    Set up slider
 */
function setSlider() {
    const query = '/slider';
    fetch(query)
        .then(response => response.json())
        .then(json => {
            // Set up attributes of slider
            $('#time-select').attr('min', json.min);
            $('#time-select').attr('max', json.max);
            $('#time-select').attr('value', json.min);
            //display current time
            startTime.setHours(parseInt(json.start[0]), parseInt(json.start[1]), parseInt(json.start[2]), parseInt(json.start[3]));
            $('#sliderdisplay').text(startTime.toLocaleTimeString());
            //set slider circle to current time
            $('#time-select').val(parseInt(json.start[3]));
            //set up function to change display on change of slider
            $('#time-select').mouseup(function () {
                $.post('/select-offset', {new_value: this.value},
                        function (response) {
                    displayData(0);
                    let newTime = new Date();
                    newTime.setHours(startTime.getHours(), startTime.getMinutes(), startTime.getSeconds());
                    newTime.setMilliseconds($('#time-select').val());
                     $('#sliderdisplay').text(newTime.toLocaleTimeString());
                });

            })
        })
        .then(function () {
            $('#sliderdisplay').show();
            $('.slidecontainer').show();
        });
}
