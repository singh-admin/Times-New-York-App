document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const searchPage = document.getElementById('searchPage');
    let userId = '';
  
    loginForm.addEventListener('submit', function(event) {
      event.preventDefault();
      const username = document.getElementById('username').value;
      const password = document.getElementById('password').value;

      fetch('http://127.0.0.1:5000/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ username, password })
    })
    .then(response => response.json())
    .then(data => {
      if (data.user_id) {
        // If login is successful, hide the login page and show the search page
        userId = data.user_id;
        loginPage.style.display = 'none';
        searchPage.style.display = 'block';
      } else {
        // If login fails, display an error message
        // alert('Invalid username or password');
      }
    })
    .catch(error => {
      console.error('Error logging in:', error);
    });
  
      loginPage.style.display = 'none';
      searchPage.style.display = 'block';
      userId = 1;
    });
  
    const searchInput = document.getElementById('searchInput');
    const searchResults = document.getElementById('searchResults');
  
    searchInput.addEventListener('input', function() {
      const query = searchInput.value.trim();
  
      fetch(`http://127.0.0.1:5000/search?q=${query}&user_id=${userId}`)
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => {
        // Check if the expected data structure is received
        if (!data.articles || !data.articles.response || !Array.isArray(data.articles.response.docs)) {
          console.error('Unexpected data structure received:', data);
          throw new Error('Unexpected data structure');
        }
    
        const articleResults = data.articles.response.docs;
    
        // Display the article search results
        articleResults.forEach(article => {
          const resultElement = document.createElement('div');
          resultElement.textContent = article.headline.main; 
          resultElement.addEventListener('click', function() {
            articleTitle.textContent = article.headline.main;
            articleContent.textContent = article.abstract; 
            articleDetails.style.display = 'block';
          });
          searchResults.appendChild(resultElement);
        });
      })
      .catch(error => {
        console.error('Error fetching or processing search results:', error);
      });
    
});
});
 



