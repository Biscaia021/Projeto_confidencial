import { observeCards } from './animations.js';
import { loadGitHubRepos } from './github.js';
import { initAiChat } from './ai-chat.js';

document.addEventListener('DOMContentLoaded', () => {
    observeCards();
    loadGitHubRepos('biscaia021');
    initAiChat();
});

