function summarize() {
    const xhr = new XMLHttpRequest();
    const url = '/summarize-text';
    const inputText = document.getElementById('input-text').value;
    const dropdownValue = document.getElementById('dropdown').value;
    const wordCount = parseInt(document.getElementById('word-count').textContent.replace('Word Count: ', ''), 10);
    const data = {
      text: inputText,
      option: dropdownValue,
      count: wordCount
    };
    const headers = { 'Content-Type': 'application/json' };
    const wordCountElement2 = document.getElementById('word-count2');
    const wordCountElement3 = document.getElementById('word-count3');

    xhr.open('POST', url);
    xhr.setRequestHeader('Content-Type', 'application/json');

    xhr.onload = function() {
      if (xhr.status === 200) {

        const data = JSON.parse(xhr.responseText);
        const var1 = data.summary1;
        const var2 = data.summary2;
        const time = data.time

        document.getElementById('output-text1').value = var1;
        document.getElementById('output-text2').value = var2;
        document.getElementById('time').value = time;

        const wordCount1 = countWords(document.getElementById('output-text1'));
        document.getElementById('word-count2').textContent = 'Word Count: ' + wordCount1;
        const wordCount2 = countWords(document.getElementById('output-text2'));
        document.getElementById('word-count3').textContent = 'Word Count: ' + wordCount2;

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


  function save() {
    const xhr = new XMLHttpRequest();
    const url = '/save_summarization';

    const input = document.getElementById('input-text').value;
    const output1 = document.getElementById('output-text1').value;
    const output2 = document.getElementById('output-text2').value;
    const title = document.getElementById("title").value;

    const currenturl = window.location.href;
    const queryString = currenturl.split('?')[1];
    const searchParams = new URLSearchParams(queryString);
    const folderId = searchParams.get('folder_id');
    const data = { input: input, output1: output1, output2: output2, folder_id: folderId, title: title};
    const headers = { 'Content-Type': 'application/json' };

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

  function countWords(textareavar) {
    const text = textareavar.value.trim();
  
    const words = text.split(/\s+/);
  
    const filteredWords = words.filter(word => word !== '');
  
    return filteredWords.length;
  }
  function goBack() {
    const currenturl = window.location.href;
    const queryString = currenturl.split('?')[1];
    const searchParams = new URLSearchParams(queryString);
    const folderId = searchParams.get('folder_id');
    window.location.href = '/userhome/' + folderId;

  }


  
  
  
  