//let startTime = new Date();
///*
// Fetch selected electrode data
// */
//function displayData(delta=0) {
//    const query = '/data?delta=' + delta.toString();
//    console.log(query);
//    fetch(query)
//            .then(response => response.json())
//            .then(json => {
//                const graphs = document.getElementById('time_series');
//                let data_maps = [];
//                for (let id in json.data) {
//                    data_maps.push(createDataObject(json.data[id][1], json.data[id][0]));
//                }
//                if (!graphs.hasChildNodes()) {
//                    $('#time_series').append(graphs.appendChild(createChartElementFrom(json.time, data_maps, parseInt(json.dataOffset))));
//                } else {
//                    changeData(data_maps, json.time)
//                }
//                setSlider();
//                $('#duration').val(parseInt(json.duration));
//            });
//}
//
//
///*
// Toggle select electrode form
// Fetch electrode labels
// Dynamically add check inputs to electrode form for each electrode
// */
//function openElectrodeSelect() {
//    $('#electrode_form').slideToggle();
//    fetch('/electrode_get')
//            .then(response => response.json())
//            .then(json => {
//                //Delete all checkboxes except for label in form
//                $('#electrode_form').empty();
//
//                Object.keys(json.values).forEach( id=> {
//                    $('#electrode_form').append(getElectrodeSelectElement(id,json.values[id].trim()))
//                });
//                const submit = document.createElement('input');
//                submit.setAttribute('type', 'submit');
//                submit.setAttribute('onClick', 'openElectrodeSelect();')
//                $('#electrode_form').append(submit);
//                $('#electrode_form').append(document.createElement('br'));
//                saveElectrodeSelect();
//            });
//}
////remove unselected charts
//function removeUnselected() {
//    fetch('/electrode_select')
//        .then(response => response.json())
//        .then(json=> {
//            Object.keys(charts).forEach(key => {
//                if (!json.data.includes(key)) {
//                    delete charts[key];
//                    document.getElementById(key).remove();
//                }
//            });
//        })
//}
//
////save the state of the checkboxes
//function saveElectrodeSelect() {
//    fetch('/electrode_select')
//        .then(response => response.json())
//        .then(json=> {
//            var val;
//            console.log(json);
//
//            for (val in json.data) {
//                let str = json.data[val].toString().trim();
//                console.log(str);
//                document.getElementById(str).checked = true;
//                }
//        })
//}
//
//
///*
//  Display annotations
// */
//function toggleAnnotate() {
//    const query = '/ann_data';
//    fetch(query).then(response => response.json()).then(json => {
//        const amplitude = parseInt(json.amplitude);
//        if (!('annotations' in chart.options.annotation)) {
//            let index;
//            let anns = [];
//            for (index in json.annotations) {
//                const annotation_config = {
//                    type: 'box',
//                    mode: 'vertical',
//                    xScaleID: 'x-axis-0',
//                    yScaleID: 'y-axis-0',
//                    scaleID: 'x-axis-0',
//                    // Left edge of the box. in units along the x axis
//                    xMin: json.annotations[index]['start'],
//                    xMax: json.annotations[index]['end'],
//                    yMax: parseInt(json.annotations['chart_max']),
//                    yMin: parseInt(json.annotations['chart_min']),
//                    content: "Test label",
//                    borderColor: 'grey',
//                    borderWidth: 0,
//                }
//                anns.push(annotation_config);
//            }
//            chart.options.annotation = { annotations: anns };
//        }
//        else {
//            delete chart.options.annotation['annotations'];
//        }
//        chart.update();
//    });
//}
//
//
///*
//  Change amplitude by 100 up/down
// */
//function alterAmplitudes(delta) {
//    const query = '/amplitude?delta=' + delta.toString();
//    fetch(query).then(response => response.json()).then( json => {
//        const amplitude = parseInt(json.amplitude);
//        const newMax = parseInt(json.newMax);
//        const newMin = parseInt(json.newMin);
//        chart.options.scales.max = newMax;
//        chart.options.scales.min = newMin;
//        chart.options.scales.yAxes[0].ticks.stepSize = amplitude;
//        chart.update(0)
//        displayData(0);
//    });
//}
//
///*
//    Set up slider
// */
//function setSlider() {
//    const query = '/slider';
//    fetch(query)
//        .then(response => response.json())
//        .then(json => {
//            $('#time-select').attr('min', json.min);
//            $('#time-select').attr('max', json.max);
//            $('#time-select').attr('value', json.min);
//            startTime.setHours(parseInt(json.start[0]), parseInt(json.start[1]), parseInt(json.start[2]), parseInt(json.start[3]));
//            $('#sliderdisplay').text(startTime.toLocaleTimeString());
//            $('#time-select').val(parseInt(json.start[3]));
//
//            $('#time-select').mouseup(function () {
//                $.post('/select-offset', {new_value: this.value},
//                        function (response) {
//                    displayData();
//                    let newTime = new Date();
//                    newTime.setHours(startTime.getHours(), startTime.getMinutes(), startTime.getSeconds());
//                    console.log(this.value);
//                    console.log(typeof this.value);
//                    newTime.setMilliseconds($('#time-select').val());
//                     $('#sliderdisplay').text(newTime.toLocaleTimeString());
//                });
//
//            })
//        });
//}