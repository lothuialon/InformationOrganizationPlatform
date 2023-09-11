const textarea = document.getElementById('input-text');

const wordCountElement = document.getElementById('word-count');


function countWords(textareavar) {
  const text = textareavar.value.trim();

  const words = text.split(/\s+/);

  const filteredWords = words.filter(word => word !== '');

  return filteredWords.length;
}

textarea.addEventListener('input', function() {
    const wordCount = countWords(textarea);
    wordCountElement.textContent = 'Word Count: ' + wordCount;
});


