let dropZone = document.querySelector('#drop-zone');
let dragElements = document.querySelector('#drag-elements');

let isDropped = false;
let isOut = false;

var drake = dragula(
    [
        dragElements,
        dropZone
    ],
    {
        copy: true, //Elements are cloned
        removeOnSpill: true, // Elements can be deleted on dropping outside the container
        copySortSource: true

    }).on('drop', function (el, target, source, sibling) {
    isDropped = true;
    children = dropZone.querySelectorAll('[data-mjml-id]');
    mjml = document.getElementById("mjml");
    mj_body = document.getElementById('mj-body');
    mj_body.innerHTML = "";

    children.forEach(function (child) {
        var mjmlId = child.dataset.mjmlId;
        console.log("Children", child);
        mjml_element = document.getElementById(mjmlId).innerHTML;
        mj_body.insertAdjacentHTML('beforeend', mjml_element);
    });

    makeRequest(mjml.innerHTML);

}).on('out', function (el, container, source) {
    isOut = true;
    console.log("Element", el, "container", container, "Source", source, "Is Dropped:", isDropped, "Is Out:", isOut);
}).on('over', function () {
    isOut = false;
}).on('drag', function () {
    isDropped = false;
}).on("dragend", function () {
    isDropped = true;
    console.log("Dropped", isDropped, "Out", isOut);
});


function makeRequest(mjml) {
    // Define the base URL
    const baseUrl = 'https://api.mjml.io/v1/render';

    // Define the App ID and Secret
    const APP_ID = '4f1df938-16bd-416b-8637-e26a7b1d2c23';
    const SECRET = 'babbe6b2-e59a-432c-a892-be4eadfd3426';

    /// Create the payload for the POST request
    const payload = {
        mjml: mjml
    };

    // Create the HTTP headers with the basic auth
    const headers = {
        "Authorization": "Basic " + btoa(APP_ID + ':' + SECRET),
        "Content-Type": "application/json"
    };

    fetch(baseUrl, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify(payload)
    })
        .then(response => response.json())
        .then(data => {
            // Handle the success response here
            injectContent(data);
        })
        .catch(error => {
            // Handle the error response here
            console.log('Error:', error);
        });
}

function injectContent(data) {
    // First, empty the target elements
    const htmlTargetElement = document.getElementById('html');
    // const mjmlTargetElement = document.getElementById('mj-body');
    htmlTargetElement.innerHTML = "";
    // mjmlTargetElement.innerHTML = "";

    // Then, inject the content
    htmlTargetElement.innerHTML = data.html;
    // mjmlTargetElement.innerHTML = data.mjml;
}
