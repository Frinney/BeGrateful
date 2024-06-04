import { setupGratitude } from './components/gratitude/gratitude.js';
import { setupProfile } from './components/profile/profile.js';
import { setupFriends } from './components/friend/friend.js';
import { setupGlobal } from './components/global/global.js';

document.addEventListener('DOMContentLoaded', () => {
  // Ініціалізація різних частин додатку
  setupGratitude();
  setupProfile();
  setupFriends();
  setupGlobal();
});