// Collector JS Logic

let currentPage = 1;
const perPage = 5;

function toggleTextField(selectElement) {
  const newDatasetInput = document.getElementById('new_dataset_input');
  if (selectElement.value === 'new') {
    newDatasetInput.style.display = 'block';
  } else {
    newDatasetInput.style.display = 'none';
  }
}

function fetchSamples(datasetName, page) {
  const samplesDiv = document.getElementById('samples');
  currentPage = page;
  fetch(`/samples?dataset_name=${datasetName}&page=${page}&per_page=${perPage}`)
    .then(response => response.json())
    .then(data => {
      let samplesHtml = '<h3>Latest Samples</h3>';
      if (data.samples.length > 0) {
        samplesHtml += '<ul>';
        data.samples.forEach(sample => {
          samplesHtml += `<li><strong>Input:</strong> ${sample.input_data} <br> <strong>Output:</strong> ${sample.output_data}</li>`;
        });
        samplesHtml += '</ul>';
      } else {
        samplesHtml += '<p>No samples available for this dataset.</p>';
      }

      // Pagination Controls
      samplesHtml += '<div>';
      if (currentPage > 1) {
        samplesHtml += `<button onclick="fetchSamples('${datasetName}', ${currentPage - 1})">Previous</button>`;
      }
      if (currentPage < data.total_pages) {
        samplesHtml += `<button onclick="fetchSamples('${datasetName}', ${currentPage + 1})">Next</button>`;
      }
      samplesHtml += '</div>';

      samplesDiv.innerHTML = samplesHtml;
    })
    .catch(error => {
      samplesDiv.innerHTML = `<p style="color:red;">Error fetching samples: ${error.message}</p>`;
    });
}

function onDatasetSelectChange(selectElement) {
  toggleTextField(selectElement);
  if (selectElement.value !== 'new') {
    fetchSamples(selectElement.value, 1);
  } else {
    document.getElementById('samples').innerHTML = '';
  }
}

function deleteExample(exampleId) {
  fetch('/delete_example', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: `id=${exampleId}`
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      document.getElementById(`example-${exampleId}`).remove();
    } else {
      alert("Failed to delete the example.");
    }
  });
}

function validateForm() {
  const datasetSelect = document.getElementById('dataset_name_select');
  const newDatasetInput = document.getElementById('new_dataset_name');
  let datasetName = '';

  if (datasetSelect.value === 'new') {
    datasetName = newDatasetInput.value.trim();
  } else {
    datasetName = datasetSelect.value;
  }

  if (!datasetName) {
    alert('Please provide a valid dataset name.');
    return false; // Prevent form submission
  }

  return true; // Allow form submission
}
