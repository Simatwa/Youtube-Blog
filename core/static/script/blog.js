function formatTimeAgo(datetimeStr) {
  var datetime = new Date(datetimeStr);
  var now = new Date();
  var utcNow = new Date(now.getTime() + now.getTimezoneOffset() * 60000);
  var diff = utcNow - datetime;

  var minute = 60 * 1000;
  var hour = 60 * minute;
  var day = 24 * hour;
  var month = 30 * day;
  var year = 365 * day;

  if (diff < minute) {
    var seconds = Math.floor(diff / 1000);
    return seconds + ' Second' + (seconds === 1 ? '' : 's') + ' ago';
  } else if (diff < hour) {
    var minutes = Math.floor(diff / minute);
    return minutes + ' Minute' + (minutes === 1 ? '' : 's') + ' ago';
  } else if (diff < day) {
    var hours = Math.floor(diff / hour);
    return hours + ' Hour' + (hours === 1 ? '' : 's') + ' ago';
  } else if (diff < month) {
    var days = Math.floor(diff / day);
    return days + ' Day' + (days === 1 ? '' : 's') + ' ago';
  } else if (diff < year) {
    var months = Math.floor(diff / month);
    return months + ' Month' + (months === 1 ? '' : 's') + ' ago';
  } else {
    var years = Math.floor(diff / year);
    return years + ' Year' + (years === 1 ? '' : 's') + ' ago';
  }
}

function formatTimeAgoShort(datetimeStr) {
  var datetime = new Date(datetimeStr);
  var now = new Date();
  var utcNow = new Date(now.getTime() + now.getTimezoneOffset() * 60000);
  var diff = utcNow - datetime;

  var minute = 60 * 1000;
  var hour = 60 * minute;
  var day = 24 * hour;
  var month = 30 * day;
  var year = 365 * day;

  if (diff < minute) {
    var seconds = Math.floor(diff / 1000);
    return seconds + ' Sec' + (seconds === 1 ? '' : 's') + ' ago';
  } else if (diff < hour) {
    var minutes = Math.floor(diff / minute);
    return minutes + ' Min' + (minutes === 1 ? '' : 's') + ' ago';
  } else if (diff < day) {
    var hours = Math.floor(diff / hour);
    return hours + ' Hr' + (hours === 1 ? '' : 's') + ' ago';
  } else if (diff < month) {
    var days = Math.floor(diff / day);
    return days + ' Dy' + (days === 1 ? '' : 's') + ' ago';
  } else if (diff < year) {
    var months = Math.floor(diff / month);
    return months + ' Mon' + (months === 1 ? '' : 's') + ' ago';
  } else {
    var years = Math.floor(diff / year);
    return years + ' Yr' + (years === 1 ? '' : 's') + ' ago';
  }
}

function AddSubscription() {
  var submitButton = document.getElementById("subscriptionButton");
  submitButton.disabled = true; // Disable the submit button
  const formElement = document.getElementById('subscriptionForm');
  const dataInput = document.getElementById('email');
  const url = formElement.getAttribute('action');
  const formData = new FormData();
  formData.append('email', dataInput.value);
  const xhr = new XMLHttpRequest();
  xhr.open(formElement.getAttribute('method'), url, true);
  xhr.onload = function() {
    const displayElement = document.getElementById('subscriptionResponse');
    const response = JSON.parse(xhr.responseText);
    const message = response.message;
    if (xhr.status === 200) {
      displayElement.innerHTML = `
        <div class="w3-middle w3-panel w3-display-container w3-pale-green w3-leftbar w3-border w3-border-green w3-round w3-animate-zoom" id="alertNotch254">
          <h4 class="w3-strong w3-text-blue">Note!</h4>
          <button class="w3-display-topright w3-large w3-btn w3-transparent" onclick="w3.hide('#alertNotch254')">
            &times;
          </button>
          <p>${message}</p>
        </div>`;
    } else {
      displayElement.innerHTML = `
        <div class="w3-middle w3-panel w3-display-container w3-pale-yellow w3-leftbar w3-border w3-border-yellow w3-round w3-animate-zoom" id="alertNotch255">
          <h4 class="w3-strong w3-text-blue">Warn!</h4>
          <button class="w3-display-topright w3-large w3-btn w3-transparent" onclick="w3.hide('#alertNotch255')">
            &times;
          </button>
          <p>${message}</p>
        </div>`;
    }
    submitButton.disabled = false;
  };
  xhr.onerror = function() {
    console.error('Request failed');
  };
  xhr.send(formData);
}


// Get the form element by ID
//const form = document.getElementById('mobileSearch');

// Trigger the function on form submission
//form.addEventListener('keyup', handleSubmit);

// Handle form submission
function handleSubmit() {
  //event.preventDefault(); // Prevent form submission

  // Get the input value
  const inputValue = document.querySelector('input[id="mobileSearchQuery"]').value;
  const outputDiv = document.getElementById('mobileSearchDisplay');
  
  if (inputValue === "") {
     outputDiv.style.display = 'none';
    return 
  }

  const form = document.getElementById('mobileSearch');

  // Get the form action URL
  const actionUrl = form.action;

  // Create a new XMLHttpRequest object
  const xhr = new XMLHttpRequest();

  // Set up the request
  xhr.open('GET', `${actionUrl}?q=${inputValue}`, true);

  // Set the response type
  xhr.responseType = 'json';

  // Define the onload callback function
  xhr.onload = function() {
    if (xhr.status === 200) {
      // Generate HTML based on the response data
      const result = xhr.response.result;
      const html = generateHTML(result);

      // Display the generated HTML
      outputDiv.innerHTML = html;
      outputDiv.style.display = 'block'
    } else {
      console.error('Request failed. Status:', xhr.status);
    }
  };

  // Send the request
  xhr.send();
}

// Generate HTML based on the response data
function generateHTML(result) {
  let html = '';
  result.forEach(item => {
    html += `
    <div class="w3-display-container">
    <button class="w3-display-topright w3-btn w3-transparent w3-text-black" onclick="this.parentElement.style.display='none'">&times</button>
    <p class="w3-text-red w3-pale-yellow w3-border w3-round w3-padding">
        <a href="${item[0]}">${item[1].replace(/[^\x00-\x7F]/g, "")}
        </a></p>
      </div>
        `;
  });
  return html;
}

function requests(method, url, cFunction) {
  // Makes requests                               
  const xhttp = new XMLHttpRequest();             
  xhttp.onload = function() {cFunction(this);}    
  xhttp.open(method, url);                        
  xhttp.send();
}        
                                       
function displayLikeCount(resp){
  //Displays new like count
  const likes = JSON.parse(resp.responseText);
  const likes_count_display_area = document.getElementById('likesCount');
  likes_count_display_area.innerHTML = likes.count;
}

function addLike(url){
  //Change color
  const like_button = document.getElementById('likeBlog');
  like_button.style.color = 'red';
  like_button.disabled = true;
  requests('GET', url, displayLikeCount);
}



function requests_with_arg(method, url, cFunction, commentId) {
  // Makes requests and parse arg to function                               
  const xhttp = new XMLHttpRequest();             
  xhttp.onload = function() {cFunction(this, commentId);}    
  xhttp.open(method, url);                        
  xhttp.send();
}

function displayCommentLikes(resp, commentId){
// Displays new comment likes
  const like_display_space = document.getElementById(commentId);
  const comment = JSON.parse(resp.responseText);
  like_display_space.innerHTML = comment.count; 
}

function addCommentLike(url, commentId){
// Initiates comment's + count
  const like_button = document.getElementById('btn-' + commentId);
  like_button.style.color = 'red';
  like_button.disabled = true;
  requests_with_arg('GET', url, displayCommentLikes, commentId);
}

// Load more

function displayMoreContent(resp){
  const response = JSON.parse(resp.responseText);
  // Hide the load more button
  const spinner = document.getElementById("loadMoreSpinner");
  spinner.style.display = 'none';
  
  if (response.is_complete)
  {
  const load_more_button = document.getElementById('loadMoreButton');
  load_more_button.disabled = true;
  load_more_button.style.color = 'red';
  load_more_button.innerHTML = 'No more';
  
  }
  //Display content
  else 
  {
   const load_more_display_area = document.getElementById('displayMoreSearch');
   const previously_loaded_content = load_more_display_area.innerHTML;
   load_more_display_area.innerHTML = previously_loaded_content + response.content;
  }
  
}

// triggers load more
function loadMore(url){
  const spinner = document.getElementById("loadMoreSpinner");
  spinner.style.display = 'block';
  requests('POST', url, displayMoreContent);
}