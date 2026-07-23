import { observeCards } from './animations.js';

export function loadGitHubRepos(githubUsername) {
    const grid = document.getElementById('projects-grid');
    if (!grid) return;

    const cacheKey = `github_repos_v2_${githubUsername}`;
    const cachedData = sessionStorage.getItem(cacheKey);

    if (cachedData) {
        renderRepos(JSON.parse(cachedData), grid);
    } else {
        fetch(`https://api.github.com/users/${githubUsername}/repos?sort=updated&per_page=100`)
            .then(response => response.json())
            .then(repos => {
                sessionStorage.setItem(cacheKey, JSON.stringify(repos));
                renderRepos(repos, grid);
            })
            .catch(error => console.error('Error fetching repos:', error));
    }
}

function renderRepos(repos, grid) {
    grid.innerHTML = '';
    
    const fragment = document.createDocumentFragment();
    const ignoredRepos = ['pokedex', 'https-biscaia021.github.io', 'biscaia021', 'biscaia021.github.io', 'nlp', 'biometria_facial'];

    repos.forEach(repo => {
        if (repo.fork || ignoredRepos.includes(repo.name.toLowerCase())) return;

        const article = document.createElement('article');
        article.className = 'card';
        
        const description = repo.description ? repo.description : 'No description available.';
        const language = repo.language ? `<span style="color: var(--accent-color); font-size: 0.85rem; display: block; margin-bottom: 10px;">#${repo.language}</span>` : '';

        article.innerHTML = `
            <div class="card-img" style="background: rgba(255,255,255,0.05); display: flex; align-items: center; justify-content: center;">
                <img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" alt="GitHub Logo" style="width: 50px; opacity: 0.7; filter: invert(1);">
            </div>
            <h3>${repo.name}</h3>
            ${language}
            <p>${description}</p>
            <div style="margin-top: auto; padding-top: 15px;">
                <a href="${repo.html_url}" target="_blank" class="btn">View on GitHub</a>
            </div>
        `;
        
        fragment.appendChild(article);
    });
    
    grid.appendChild(fragment);
    observeCards();
}
