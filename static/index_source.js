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
                console.log(JSON.stringify(json));
                const context = document.getElementById('graph');
                var chart = new Chart
            });
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
