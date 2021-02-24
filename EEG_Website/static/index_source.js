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
        displayData();
    }
}

/*
 Fetch selected electrode data
 */
function displayData() {
    fetch('/data')
            .then(response => response.json())
            .then(json => {
                console.log(Object.keys(json.data));
                // Object.keys(json.data).forEach( id=> {
                //     console.log(id);
                // })
                let data_maps = []
                let id;

                for (id in Object.keys(json.data)) {
                    const name = Object.keys(json.data)[id];
                    console.log(name);
                    let data_map = {};
                    data_map['label'] = name;
                    data_map['data'] = json.data[name].map(Number);
                    data_maps.push(data_map);
                }
                const context = document.getElementById('graph');
                let ctx = document.getElementById("graph").getContext('2d');
                let myChart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: json.time,
                        datasets: data_maps
                        //     [{
                        //     label: 'Time series',
                        //     data: json.data['EEG E1-REF1     '].map(Number),
                        // }]
                    },
                });
            })

}



/*
 Toggle select file form
 */
function openFileSelect() {
    const fileForm = document.getElementById('file_form');
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
