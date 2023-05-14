window.onload = function () {
    // Read /status
    var req = new XMLHttpRequest();
    req.open('GET', '/status', true);
    req.onload = function () {
        if (req.status >= 200 && req.status < 400) {
            // Success!
            var jobs = JSON.parse(req.responseText)['tasks'];
            var joblist = document.getElementById('running_jobs');
            for (var i = 0; i < jobs.length; i++) {
                // Append to the ul
                var li = document.createElement('li');
                li.className = 'list-group-item';
                li.textContent = jobs[i];
                // if it is the last job color it green
                if (i == jobs.length - 1) {
                    li.style.color = 'green';
                }
                joblist.appendChild(li);
            }
        }
    };
    req.send();

    // refresh the entire page every 5 seconds
    setInterval(function () {
        window.location.reload();
    }, 5000);
};