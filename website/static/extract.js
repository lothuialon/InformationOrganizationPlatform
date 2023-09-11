function extract() {
    const xhr = new XMLHttpRequest();
    const url = '/extract-keyword';
    const inputText = document.getElementById('input-text').value;
    const keywordNum = document.getElementById('keywordNum').value;
    const data = {
      text: inputText,
      number: keywordNum
    };

    xhr.open('POST', url);
    xhr.setRequestHeader('Content-Type', 'application/json');

    xhr.onload = function() {
      if (xhr.status === 200) {

        const data = JSON.parse(xhr.responseText);
        const var1 = data.keywords;


        document.getElementById('output-text').value = var1;


        var targetButton = document.getElementById("button1");
        targetButton.style.display = "inline-block";
        document.getElementById("titleText").style.display = "inline"
        document.getElementById("title").style.display = "inline"
      } else {
        console.log('Error:', xhr.status);
      }
    };

    xhr.onerror = function() {
      console.log('Error:', xhr.status);
    };

    xhr.send(JSON.stringify(data));
  }

  function saveKeyword() {
    const xhr = new XMLHttpRequest();
    const url = '/save_keywords';

    const input = document.getElementById('input-text').value;
    const output = document.getElementById('output-text').value;
    const title = document.getElementById('title').value
    const currenturl = window.location.href;
    const queryString = currenturl.split('?')[1];
    const searchParams = new URLSearchParams(queryString);
    const folderId = searchParams.get('folder_id');
    const data = { input: input, output: output, folder_id: folderId, title: title};
    const headers = { 'Content-Type': 'application/json' };
    console.log(title)

    xhr.open('POST', url);
    xhr.setRequestHeader('Content-Type', 'application/json');

    xhr.onload = function() {
      if (xhr.status === 200) {

        console.log('Success:', xhr.status)
      
        setTimeout(3000)
        goBack();

      } else {
        console.log('Error:', xhr.status);
      }
    };

    xhr.onerror = function() {
      console.log('Error:', xhr.status);
    };

    xhr.send(JSON.stringify(data));
  }

function goBack() {
    const currenturl = window.location.href;
    const queryString = currenturl.split('?')[1];
    const searchParams = new URLSearchParams(queryString);
    const folderId = searchParams.get('folder_id');
    window.location.href = '/userhome/' + folderId;

  }