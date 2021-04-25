// Global object which will indicate the start of data recording for use with timeslider
let startTime = new Date();
/*
    Handle ml model
*/

function startModel() {
    $('#reference-input').show();
    $('#reference-input').change(function () {
        const val = $('#reference-input').val().toString();
        const query = '/model?ref-index=' + val; //TODO: Add args
        const source = new EventSource(query);
        $('#reference-input').hide();
        source.addEventListener('update', function (event) {
            console.log(event);
        });
        source.addEventListener('close', function (event) {
            console.log("closing event listener");
            source.close();
            alert("Model Successful: Ready for prediction");
        });
    });
}

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
                    $('#time_series').append(createChartElementFrom(json.time, data_maps, parseInt(json.dataOffset), json.update));
                }
                // else update current chart with new configurations and time labels
                else {
                    changeData(data_maps, json.time, parseInt(json.dataOffset),json.update)
                }
                // Update duration display
                $('#duration').val(parseInt(json.duration));
                return json.update;
            })
        .then(function (update) {
            setSlider();
            $('#time-select').val(update.sliderval);
            $('#sliderdisplay').show();
            $('.slidecontainer').show();
            const duration_qry = '#duration-input option[value=\''+ update.duration+ '\']';
            $(duration_qry).prop('selected', true);
            const filter_qry = '#filter-input option[value=\''+ update.filter + '\']';
            $(filter_qry).prop('selected', true);
            renderAnnotations();
        });
        fetch("/subject")
        .then(response=>response.json())
        .then(json => {
            for (let index in json.references) {
                const ref = json.references[index];
                const option = $('<option></option>', {val:ref.id});
                option.text(ref.label);
                $('#reference-input').append(option);
            }
        })
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
            for (let val in json.data) {
                let str = json.data[val].toString().trim();
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
                    start:start,
                    end:end,
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
        chart.update(0);
        renderAnnotations();
    });
}

// List annotation in right side bar
function getAnnotationsToList() {
    const query = '/ann_data?byTime=false';
    fetch(query).then(response => response.json()).then(json => {
        for (let index in json.annotations) {
            // Calculate offset to jump to when selected (currently .3 of selected duration ahead of annotation onset to the nearest second)
            const onset = parseInt(json.annotations[index]['Onset']);
            const duration = parseInt(json.annotations[index]['Duration']);
            const display_duration = parseInt(json.duration)
            let start = onset - Math.floor(.3 * display_duration)
            start = (start > 0) ? start : 0;

            const label = json.annotations[index]['Annotation'];
            // create and append annotation item to right sider bar
            $('#annotation-items').append(createAnnotationElementFrom(label, start, duration));
        }
        $('div.card').mouseenter( function () {
            $(this).addClass("card bg-dark text-white");
        }).mouseleave( function () {
            $(this).removeClass("card bg-dark text-white");
            $(this).addClass("card");
        })
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
        chart.update()
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
            startTime.setHours(parseInt(json.start[0]));
            startTime.setMinutes(parseInt(json.start[1]));
            startTime.setSeconds(parseInt(json.start[2]));
            // Set up attributes of slider
            $('#time-select').attr('min', json.min);
            $('#time-select').attr('max', json.max);
            $('#time-select').attr('value', json.min);
        });
}
