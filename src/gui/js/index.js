window.onload = function () {
    // Get the library_table table in the document
    var libraryTable = document.getElementById('library_table');
    // Get the Library at /library
    var req = new XMLHttpRequest();
    req.open('GET', '/library', true);
    req.onload = function () {
        if (req.status >= 200 && req.status < 400) {
            // Success!
            var row = libraryTable.insertRow(0);
            var library = JSON.parse(req.responseText);
            for (var i = 0; i < library.length; i++) {
                // Add content to the table
                var row = libraryTable.insertRow(i + 2);
                var name = row.insertCell(0);
                var bundleID = row.insertCell(1);
                var version = row.insertCell(2);

                var actions = row.insertCell(3);
                actions.setAttribute('style', 'flex-direction: row; display: flex;');

                var update_button = document.createElement('button');
                update_button.setAttribute('class', 'btn btn-primary bg-dark');
                update_button.setAttribute('style', 'margin: 5px;');
                update_button.setAttribute('type', 'button');
                update_button.setAttribute('onclick', 'updateIPA("' + library[i].bundleID + '")');
                update_button.innerHTML = '<i class="bi bi-download"></i>';
                update_button.setAttribute('title', '(Re)Download IPA');

                var decrypt_button = document.createElement('button');
                decrypt_button.setAttribute('class', 'btn btn-primary bg-dark');
                decrypt_button.setAttribute('style', 'margin: 5px;');
                decrypt_button.setAttribute('type', 'button');
                decrypt_button.setAttribute('onclick', 'decryptIPA("' + library[i].bundleID + '")');
                decrypt_button.innerHTML = '<i class="bi bi-unlock"></i>';
                decrypt_button.setAttribute('title', 'Decrypt IPA');

                name.innerHTML = library[i].name;
                bundleID.innerHTML = library[i].bundleID;
                version.innerHTML = library[i].version;
                actions.appendChild(update_button);
                actions.appendChild(decrypt_button);
            }

        } else {
            // We reached our target server, but it returned an error
            console.log('Error');
        }
    }
    req.onerror = function () {
        // There was a connection error of some sort
        console.log('Connection error');
    }
    req.send();
}

function updateIPA(id) {
    // Call /ipa/download?bundle_id=...
    var req = new XMLHttpRequest();
    req.open('POST', '/ipa/download?bundle_id=' + id, true);
    req.onload = function () {
        if (req.status >= 200 && req.status < 400) {
            // Success!
            var library = JSON.parse(req.responseText);
            console.log(library);
            alert('Job submitted!')
        } else {
            // We reached our target server, but it returned an error
            console.log('Error');
            alert('Error submitting job!')
        }
    }
    req.onerror = function () {
        // There was a connection error of some sort
        console.log('Connection error');
        alert('Error submitting job!')
    }
    req.send();
}

function decryptIPA(id) {
    // Call /decrypt with JSON body
    var request_body = {
        "bundle_id": id,
        "blacklist": []
    }
    var req = new XMLHttpRequest();
    req.open('POST', '/decrypt', true);
    req.setRequestHeader('Content-Type', 'application/json');
    req.onload = function () {
        if (req.status >= 200 && req.status < 400) {
            // Success!
            var library = JSON.parse(req.responseText);
            console.log(library);
            alert('Job submitted!')
        } else {
            // We reached our target server, but it returned an error
            console.log('Error');
            alert('Error submitting job!')
        }
    }
    req.onerror = function () {
        // There was a connection error of some sort
        console.log('Connection error');
        alert('Error submitting job!')
    }
    req.send(JSON.stringify(request_body));
}

function clearModalTable() {
    var table = document.getElementById('search-modal-table');
    var rows = table.rows.length;
    for (var i = 1; i < rows; i++) {
        table.deleteRow(1);
    }
}

const searchModal = document.getElementById('search-modal')

searchModal.addEventListener('show.bs.modal', function (event) {
    var search = document.getElementById('search-query');
    var search_value = search.value;
    
    if (search_value == '') {
        return;
    }

    // Get the table
    var table = document.getElementById('search-modal-table');

    // Get the search results
    var req = new XMLHttpRequest();
    req.open('GET', '/ipa/search?query=' + search_value, true);
    req.onload = function () {
        if (req.status >= 200 && req.status < 400) {
            var apps_result = JSON.parse(req.responseText)['apps'];
            for (var i = 0; i < apps_result.length; i++) {
                var row = table.insertRow(i + 1);
                var name = row.insertCell(0);
                var bundleID = row.insertCell(1);
                var version = row.insertCell(2);

                var actions = row.insertCell(3);
                actions.setAttribute('style', 'flex-direction: row; display: flex;');

                var update_button = document.createElement('button');
                update_button.setAttribute('class', 'btn btn-primary bg-dark');
                update_button.setAttribute('style', 'margin: 5px;');
                update_button.setAttribute('type', 'button');
                update_button.setAttribute('onclick', 'updateIPA("' + apps_result[i].bundleID + '")');
                update_button.innerHTML = '<i class="bi bi-download"></i>';
                update_button.setAttribute('title', '(Re)Download IPA');

                var decrypt_button = document.createElement('button');
                decrypt_button.setAttribute('class', 'btn btn-primary bg-dark');
                decrypt_button.setAttribute('style', 'margin: 5px;');
                decrypt_button.setAttribute('type', 'button');
                decrypt_button.setAttribute('onclick', 'decryptIPA("' + apps_result[i].bundleID + '")');
                decrypt_button.innerHTML = '<i class="bi bi-unlock"></i>';
                decrypt_button.setAttribute('title', 'Decrypt IPA');

                name.innerHTML = apps_result[i].name;
                bundleID.innerHTML = apps_result[i].bundleID;
                version.innerHTML = apps_result[i].version;
                actions.appendChild(update_button);
                actions.appendChild(decrypt_button);

                // Add content to the table
                table.appendChild(row);
            }
        } else {
            // We reached our target server, but it returned an error
            console.log('Error');
        }
    }
    req.onerror = function () {
        // There was a connection error of some sort
        console.log('Connection error');
    }
    req.send();
});


document.getElementById('search-modal').addEventListener('hidden.bs.modal', function (event) {
    clearModalTable();
});
