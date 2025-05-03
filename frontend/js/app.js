const loginPage = document.getElementById('loginPage');
const registerPage = document.getElementById('registerPage');
const dashboardPage = document.getElementById('dashboardPage');
const gotoRegister = document.getElementById('gotoRegister');
const gotoLogin = document.getElementById('gotoLogin');
const loginForm = document.getElementById('loginForm');
const registerForm = document.getElementById('registerForm');
const logoutBtn = document.getElementById('logoutBtn');
const navLinks = document.querySelectorAll('.nav-link[data-section]');
const dashboardSections = document.querySelectorAll('.dashboard-section');

// Upload Section Elements
const avatarNameInput = document.getElementById('avatarName');
const voiceNameInput = document.getElementById('voiceName');
const uploadBox = document.getElementById('uploadBox');
const fileInput = document.getElementById('fileInput');
const uploadBtn = document.getElementById('uploadBtn');
const progressContainer = document.getElementById('progressContainer');
const progressBar = document.getElementById('progressBar');
const progressStatus = document.getElementById('progressStatus');
const progressPercentage = document.getElementById('progressPercentage');

// Generate Section Elements
const scriptText = document.getElementById('scriptText');
const avatarSelect = document.getElementById('avatarSelect');
const voiceSelect = document.getElementById('voiceSelect');
const generateBtn = document.getElementById('generateBtn');
const generateProgressContainer = document.getElementById('generateProgressContainer');
const generateProgressBar = document.getElementById('generateProgressBar');
const generateProgressStatus = document.getElementById('generateProgressStatus');
const generateProgressPercentage = document.getElementById('generateProgressPercentage');

// Videos Section Elements
const videosGrid = document.getElementById('videosGrid');

// Video Modal Elements
const videoModal = document.getElementById('videoModal');
const videoModalTitle = document.getElementById('videoModalTitle');
const videoPlayer = document.getElementById('videoPlayer');
const closeVideoModal = document.getElementById('closeVideoModal');

// API Configuration
const API_BASE_URL = 'http://localhost:8000'; // Update with your actual API base URL

// Mock Data Storage
let userData = {
 avatars: [],
 voices: [],
 videos: []
};

// Initialize the App
function initApp() {
 // Load data from localStorage if exists
 const storedData = localStorage.getItem('voiceAvyData');
 if (storedData) {
 userData = JSON.parse(storedData);
 }
 
 // Check if user is logged in
 const isLoggedIn = localStorage.getItem('voiceAvyLoggedIn');
 if (isLoggedIn === 'true') {
 showPage(dashboardPage);
 updateDashboard();
 } else {
 showPage(loginPage);
 }
 
 // Setup Event Listeners
 setupEventListeners();
}

// Setup Event Listeners
function setupEventListeners() {
 // Auth Navigation - fix for anchor tags
 const registerLinks = document.querySelectorAll('a[href="register.html"]');
 registerLinks.forEach(link => {
 link.addEventListener('click', (e) => {
 e.preventDefault();
 if (registerPage) {
 showPage(registerPage);
 } else {
 window.location.href = 'register.html';
 }
 });
 });
 
 const loginLinks = document.querySelectorAll('a[href="login.html"]');
 loginLinks.forEach(link => {
 link.addEventListener('click', (e) => {
 e.preventDefault();
 if (loginPage) {
 showPage(loginPage);
 } else {
 window.location.href = 'login.html';
 }
 });
 });
 
 // Form Submissions
 if (loginForm) {
 loginForm.addEventListener('submit', handleLogin);
 }
 
 if (registerForm) {
 registerForm.addEventListener('submit', handleRegister);
 }
 
 if (logoutBtn) {
 logoutBtn.addEventListener('click', handleLogout);
 }
 
 // Dashboard Navigation
 navLinks.forEach(link => {
 link.addEventListener('click', (e) => {
 e.preventDefault();
 const sectionId = link.getAttribute('data-section');
 
 // Update active class for links
 navLinks.forEach(link => link.classList.remove('active'));
 link.classList.add('active');
 
 // Show the corresponding section
 dashboardSections.forEach(section => {
 if (section.id === sectionId) {
 section.style.display = 'block';
 } else {
 section.style.display = 'none';
 }
 });
 });
 });
 
 // Upload Section
 if (avatarNameInput && voiceNameInput && uploadBox && fileInput && uploadBtn) {
 avatarNameInput.addEventListener('input', validateUploadInputs);
 voiceNameInput.addEventListener('input', validateUploadInputs);
 uploadBox.addEventListener('click', () => fileInput.click());
 fileInput.addEventListener('change', handleFileSelect);
 uploadBtn.addEventListener('click', processUpload);
 
 // Enable drag and drop
 uploadBox.addEventListener('dragover', (e) => {
 e.preventDefault();
 uploadBox.style.borderColor = 'var(--primary-color)';
 uploadBox.style.backgroundColor = 'rgba(157, 78, 221, 0.05)';
 });
 
 uploadBox.addEventListener('dragleave', (e) => {
 e.preventDefault();
 uploadBox.style.borderColor = '#d0d0d0';
 uploadBox.style.backgroundColor = '';
 });
 
 uploadBox.addEventListener('drop', (e) => {
 e.preventDefault();
 uploadBox.style.borderColor = '#d0d0d0';
 uploadBox.style.backgroundColor = '';
 
 if (e.dataTransfer.files.length) {
 fileInput.files = e.dataTransfer.files;
 handleFileSelect();
 }
 });
 }
 
 // Generate Section
 if (scriptText && avatarSelect && voiceSelect && generateBtn) {
 scriptText.addEventListener('input', validateGenerateInputs);
 avatarSelect.addEventListener('change', validateGenerateInputs);
 voiceSelect.addEventListener('change', validateGenerateInputs);
 generateBtn.addEventListener('click', generateVideo);
 }
 
 // Video Modal
 if (closeVideoModal) {
 closeVideoModal.addEventListener('click', () => {
 videoModal.classList.remove('active');
 videoPlayer.pause();
 });
 }
}

// Page Navigation
function showPage(page) {
 if (!page) return;
 
 document.querySelectorAll('.page').forEach(p => {
 p.classList.remove('active');
 });
 page.classList.add('active');
}

// Handle Login
async function handleLogin(e) {
 e.preventDefault();
 const email = document.getElementById('loginEmail').value;
 const password = document.getElementById('loginPassword').value;
 
 // Simple validation
 if (!email || !password) {
 showToast('Please fill in all fields', 'error');
 return;
 }
 
 try {
 // Make API call to login endpoint
 const response = await fetch(`${API_BASE_URL}/login`, {
 method: 'POST',
 headers: {
 'Content-Type': 'application/json',
 },
 body: JSON.stringify({ email, password }),
 });
 
 const data = await response.json();
 
 if (!response.ok) {
 throw new Error(data.detail || 'Login failed');
 }
 
 // Save login state
 localStorage.setItem('voiceAvyLoggedIn', 'true');
 localStorage.setItem('voiceAvyUserEmail', email);
 
 // Show success message and redirect
 showToast('Login successful!', 'success');
 setTimeout(() => {
 if (dashboardPage) {
 showPage(dashboardPage);
 updateDashboard();
 } else {
 window.location.href = 'dashboard.html';
 }
 }, 1000);
 } catch (error) {
 showToast(error.message || 'Login failed', 'error');
 }
}

// Handle Register
async function handleRegister(e) {
 e.preventDefault();
 const name = document.getElementById('registerName').value;
 const email = document.getElementById('registerEmail').value;
 const password = document.getElementById('registerPassword').value;
 const confirmPassword = document.getElementById('confirmPassword').value;
 
 // Simple validation
 if (!name || !email || !password || !confirmPassword) {
 showToast('Please fill in all fields', 'error');
 return;
 }
 
 if (password !== confirmPassword) {
 showToast('Passwords do not match', 'error');
 return;
 }
 
 try {
 // Make API call to register endpoint
 const response = await fetch(`${API_BASE_URL}/register`, {
 method: 'POST',
 headers: {
 'Content-Type': 'application/json',
 },
 body: JSON.stringify({ name, email, password }),
 });
 
 const data = await response.json();
 
 if (!response.ok) {
 throw new Error(data.detail || 'Registration failed');
 }
 
 // Show success message and redirect to login
 showToast('Registration successful! Please login.', 'success');
 setTimeout(() => {
 if (loginPage) {
 showPage(loginPage);
 } else {
 window.location.href = 'login.html';
 }
 }, 1000);
 } catch (error) {
 showToast(error.message || 'Registration failed', 'error');
 }
}

// Handle Logout
function handleLogout(e) {
 e.preventDefault();
 
 // Clear login state
 localStorage.removeItem('voiceAvyLoggedIn');
 localStorage.removeItem('voiceAvyUserEmail');
 
 // Show success message and redirect
 showToast('Logged out successfully', 'info');
 setTimeout(() => {
 if (loginPage) {
 showPage(loginPage);
 } else {
 window.location.href = 'login.html';
 }
 }, 1000);
}

// Update Dashboard Data
function updateDashboard() {
 if (!dashboardPage) return;
 
 // Update avatar and voice dropdowns
 if (avatarSelect && voiceSelect) {
 updateSelectOptions(avatarSelect, userData.avatars);
 updateSelectOptions(voiceSelect, userData.voices);
 }
 
 // Update videos grid
 if (videosGrid) {
 renderVideosGrid();
 }
}

// Update Select Options
function updateSelectOptions(selectElement, options) {
 if (!selectElement) return;
 
 // Clear existing options (except first)
 while (selectElement.options.length > 1) {
 selectElement.remove(1);
 }
 
 // Add new options
 options.forEach(option => {
 const optElement = document.createElement('option');
 optElement.value = option.name;
 optElement.textContent = option.name;
 selectElement.appendChild(optElement);
 });
}

// Validate Upload Inputs
function validateUploadInputs() {
 if (!avatarNameInput || !voiceNameInput || !fileInput || !uploadBtn) return;
 
 const avatarName = avatarNameInput.value.trim();
 const voiceName = voiceNameInput.value.trim();
 const fileSelected = fileInput.files && fileInput.files.length > 0;
 
 // Check if all inputs are filled
 if (avatarName && voiceName && fileSelected) {
 // Check if names are unique
 const avatarExists = userData.avatars.some(avatar => avatar.name.toLowerCase() === avatarName.toLowerCase());
 const voiceExists = userData.voices.some(voice => voice.name.toLowerCase() === voiceName.toLowerCase());
 
 if (avatarExists) {
 avatarNameInput.style.borderColor = '#dc3545';
 } else {
 avatarNameInput.style.borderColor = '#28a745';
 }
 
 if (voiceExists) {
 voiceNameInput.style.borderColor = '#dc3545';
 } else {
 voiceNameInput.style.borderColor = '#28a745';
 }
 
 uploadBtn.disabled = avatarExists || voiceExists;
 } else {
 uploadBtn.disabled = true;
 avatarNameInput.style.borderColor = '';
 voiceNameInput.style.borderColor = '';
 }
}

// Handle File Select
function handleFileSelect() {
 if (!fileInput || !uploadBox) return;
 
 if (fileInput.files && fileInput.files.length > 0) {
 const file = fileInput.files[0];
 const fileName = file.name;
 const fileSize = (file.size / (1024 * 1024)).toFixed(2); // Convert to MB
 
 // Update upload box text
 const uploadText = uploadBox.querySelector('.upload-text');
 if (uploadText) {
 uploadText.innerHTML = `
 <p>${fileName}</p>
 <p class="small text-muted">${fileSize} MB</p>
 `;
 }
 
 // Validate inputs
 validateUploadInputs();
 }
}

// Process Upload - Updated to use the backend API
async function processUpload() {
 if (!avatarNameInput || !voiceNameInput || !fileInput || !progressContainer || !uploadBtn) return;
 
 const avatarName = avatarNameInput.value.trim();
 const voiceName = voiceNameInput.value.trim();
 const file = fileInput.files[0];
 
 if (!file) {
 showToast('Please select a video file', 'error');
 return;
 }
 
 // Show progress bar
 progressContainer.style.display = 'block';
 uploadBtn.disabled = true;
 
 // Update progress status
 progressStatus.textContent = 'Uploading and processing video...';
 progressBar.style.width = '0%';
 progressPercentage.textContent = '0%';
 
 try {
 const userId = localStorage.getItem('voiceAvyUserEmail');
 const avatarId = avatarNameInput.value;
 const audioId = voiceNameInput.value;
 
 // Create form data for API request
 const formData = new FormData();
 formData.append('video', file);
 formData.append('user_id', userId);
 formData.append('avatar_id', avatarId);
 formData.append('audio_id', audioId);
 
 // Show initial progress
 progressBar.style.width = '10%';
 progressPercentage.textContent = '10%';
 progressStatus.textContent = 'Extracting avatar and voice...';
 
 // Call the extract-for-avatar endpoint
 const response = await fetch(`${API_BASE_URL}/extract-for-avatar/`, {
 method: 'POST',
 body: formData,
 });
 
 if (!response.ok) {
 const errorData = await response.json();
 throw new Error(errorData.detail || 'Failed to process video');
 }
 
 // Update progress
 progressBar.style.width = '100%';
 progressPercentage.textContent = '100%';
 progressStatus.textContent = 'Processing completed!';
 
 // Add to data store with IDs from backend
 userData.avatars.push({ 
 name: avatarName,
 id: avatarId,
 createdAt: new Date().toISOString() 
 });
 
 userData.voices.push({ 
 name: voiceName,
 id: audioId,
 createdAt: new Date().toISOString() 
 });
 
 // Save to localStorage
 saveUserData();
 
 // Update dashboard
 updateDashboard();
 
 // Reset form
 setTimeout(() => {
 avatarNameInput.value = '';
 voiceNameInput.value = '';
 fileInput.value = '';
 const uploadText = uploadBox.querySelector('.upload-text');
 if (uploadText) {
 uploadText.innerHTML = `
 <p>Drag & drop your video here or</p>
 <div class="upload-btn">Browse Files</div>
 `;
 }
 progressContainer.style.display = 'none';
 
 // Show success message
 showToast('Avatar and voice successfully created!', 'success');
 }, 500);
 
 } catch (error) {
 // Show error
 progressStatus.textContent = 'Error: ' + error.message;
 progressBar.style.width = '100%';
 progressBar.style.backgroundColor = '#dc3545';
 
 // Reset button
 uploadBtn.disabled = false;
 
 // Show error message
 showToast('Error: ' + error.message, 'error');
 }
}

// Validate Generate Inputs
function validateGenerateInputs() {
 if (!scriptText || !avatarSelect || !voiceSelect || !generateBtn) return;
 
 const script = scriptText.value.trim();
 const avatar = avatarSelect.value;
 const voice = voiceSelect.value;
 
 // Enable button if all inputs are filled
 generateBtn.disabled = !(script && avatar && voice);
}

// Generate Video - Updated to use the backend API
async function generateVideo() {
 if (!scriptText || !avatarSelect || !voiceSelect || !generateBtn || !generateProgressContainer) return;
 
 const script = scriptText.value.trim();
 const avatarName = avatarSelect.value;
 const voiceName = voiceSelect.value;
 
 if (!script || !avatarName || !voiceName) {
 showToast('Please fill in all fields', 'error');
 return;
 }
 
 const userId = localStorage.getItem('voiceAvyUserEmail');
 
 // Show progress bar
 generateProgressContainer.style.display = 'block';
 generateBtn.disabled = true;
 
 // Set initial progress
 generateProgressBar.style.width = '0%';
 generateProgressPercentage.textContent = '0%';
 generateProgressStatus.textContent = 'Generating speech...';
 
 try {
 // Create form data for API request
 const formData = new FormData();
 formData.append('text', script);
 formData.append('user_id', userId);
 formData.append('avatar_id', avatarName);
 formData.append('audio_id', voiceName);
 
 // Update progress
 generateProgressBar.style.width = '30%';
 generateProgressPercentage.textContent = '30%';
 generateProgressStatus.textContent = 'Synthesizing voice...';
 
 // Call the generate-avatar endpoint
 const response = await fetch(`${API_BASE_URL}/generate-avatar/`, {
 method: 'POST',
 body: formData,
 });
 
 if (!response.ok) {
 const errorData = await response.json();
 throw new Error(errorData.detail || 'Failed to generate video');
 }
 
 // Get the video URL or blob from response
 const videoBlob = await response.blob();
 const videoUrl = URL.createObjectURL(videoBlob);
 
 // Update progress
 generateProgressBar.style.width = '100%';
 generateProgressPercentage.textContent = '100%';
 generateProgressStatus.textContent = 'Video generated successfully!';
 
 // Add to data store
 const videoId = 'video_' + Date.now();
 const newVideo = {
 id: videoId,
 title: `Video with ${avatarName} (${voiceName})`,
 script: script,
 avatar: avatarName,
 voice: voiceName,
 url: videoUrl, // Store the blob URL
 createdAt: new Date().toISOString(),
 duration: Math.floor(script.length / 15) + 5, // Estimate duration based on script length
 thumbnail: `/api/placeholder/${Math.floor(Math.random() * 100) + 300}/${Math.floor(Math.random() * 100) + 200}`
 };
 
 userData.videos.unshift(newVideo); // Add to beginning of array
 
 // Save to localStorage
 saveUserData();
 
 // Update dashboard
 renderVideosGrid();
 
 // Reset form
 setTimeout(() => {
 scriptText.value = '';
 avatarSelect.selectedIndex = 0;
 voiceSelect.selectedIndex = 0;
 generateProgressContainer.style.display = 'none';
 generateBtn.disabled = true;
 
 // Show success message
 showToast('Video successfully generated!', 'success');
 
 // Show the new video
 switchToVideosSection();
 }, 500);
 
 } catch (error) {
 // Show error
 generateProgressStatus.textContent = 'Error: ' + error.message;
 generateProgressBar.style.width = '100%';
 generateProgressBar.style.backgroundColor = '#dc3545';
 
 // Reset button
 generateBtn.disabled = false;
 
 // Show error message
 showToast('Error: ' + error.message, 'error');
 }
}

// Switch to Videos Section
function switchToVideosSection() {
 if (!navLinks || !dashboardSections) return;
 
 // Update active class for links
 navLinks.forEach(link => {
 const sectionId = link.getAttribute('data-section');
 if (sectionId === 'videosSection') {
 link.classList.add('active');
 } else {
 link.classList.remove('active');
 }
 });
 
 // Show the videos section
 dashboardSections.forEach(section => {
 if (section.id === 'videosSection') {
 section.classList.add('active');
 } else {
 section.classList.remove('active');
 }
 });
}

// Render Videos Grid
function renderVideosGrid() {
 if (!videosGrid) return;
 
 videosGrid.innerHTML = '';
 
 if (userData.videos.length === 0) {
 videosGrid.innerHTML = '<p class="text-center">No videos generated yet.</p>';
 return;
 }
 
 userData.videos.forEach(video => {
 const videoCard = document.createElement('div');
 videoCard.className = 'video-card';
 videoCard.innerHTML = `
 <div class="video-thumbnail">
 <img src="${video.thumbnail}" alt="${video.title}">
 <div class="video-play-icon" data-video-id="${video.id}">
 <i class="fas fa-play"></i>
 </div>
 </div>
 <div class="video-info">
 <h3 class="video-title">${video.title}</h3>
 <div class="video-meta">
 <span>${formatDate(video.createdAt)}</span>
 <span>${formatDuration(video.duration)}</span>
 </div>
 <div class="video-actions">
 <span class="video-action" data-action="play" data-video-id="${video.id}">
 <i class="fas fa-play"></i>
 </span>
 <span class="video-action" data-action="download" data-video-id="${video.id}">
 <i class="fas fa-download"></i>
 </span>
 <span class="video-action" data-action="delete" data-video-id="${video.id}">
 <i class="fas fa-trash"></i>
 </span>
 </div>
 </div>
 `;
 
 videosGrid.appendChild(videoCard);
 });
 
 // Add event listeners for video actions
 document.querySelectorAll('.video-play-icon, .video-action[data-action="play"]').forEach(el => {
 el.addEventListener('click', () => {
 const videoId = el.getAttribute('data-video-id');
 const video = userData.videos.find(v => v.id === videoId);
 if (video) {
 openVideoPreview(video);
 }
 });
 });
 
 document.querySelectorAll('.video-action[data-action="download"]').forEach(el => {
 el.addEventListener('click', () => {
 const videoId = el.getAttribute('data-video-id');
 const video = userData.videos.find(v => v.id === videoId);
 if (video) {
 // Create a download link for the video
 if (video.url) {
 const a = document.createElement('a');
 a.href = video.url;
 a.download = `${video.title}.mp4`;
 document.body.appendChild(a);
 a.click();
 document.body.removeChild(a);
 showToast('Video download started...', 'info');
 } else {
 showToast('Video URL not available', 'error');
 }
 }
 });
 });
 
 document.querySelectorAll('.video-action[data-action="delete"]').forEach(el => {
 el.addEventListener('click', () => {
 const videoId = el.getAttribute('data-video-id');
 deleteVideo(videoId);
 });
 });
}

// Open Video Preview
function openVideoPreview(video) {
 if (!videoModal || !videoModalTitle || !videoPlayer) return;
 
 videoModalTitle.textContent = video.title;
 
 // Use the actual video URL if available, otherwise use the thumbnail
 if (video.url) {
 videoPlayer.src = video.url;
 } else {
 videoPlayer.src = video.thumbnail; // Fallback to thumbnail
 }
 
 videoModal.classList.add('active');
}

// Delete Video
function deleteVideo(videoId) {
 // Get the video to delete
 const video = userData.videos.find(v => v.id === videoId);
 
 // Revoke object URL if it exists to free memory
 if (video && video.url) {
 URL.revokeObjectURL(video.url);
 }
 
 // Remove from array
 userData.videos = userData.videos.filter(v => v.id !== videoId);
 
 // Save to localStorage
 saveUserData();
 
 // Update grid
 renderVideosGrid();
 
 // Show success message
 showToast('Video deleted successfully', 'info');
}

// Save User Data
function saveUserData() {
 localStorage.setItem('voiceAvyData', JSON.stringify(userData));
}

// Show Toast Message
function showToast(message, type = 'info') {
 // Check if toast container exists, create if not
 let toastContainer = document.getElementById('toastContainer');
 if (!toastContainer) {
 toastContainer = document.createElement('div');
 toastContainer.id = 'toastContainer';
 toastContainer.className = 'toast-container';
 document.body.appendChild(toastContainer);
 }
 
 const toast = document.createElement('div');
 toast.className = `toast toast-${type}`;
 
 let icon = 'info-circle';
 if (type === 'success') icon = 'check-circle';
 if (type === 'error') icon = 'exclamation-circle';
 
 toast.innerHTML = `
 <i class="fas fa-${icon} toast-icon"></i>
 <div class="toast-message">${message}</div>
 <button class="toast-close">&times;</button>
 `;
 
 toastContainer.appendChild(toast);
 
 // Add event listener to close button
 toast.querySelector('.toast-close').addEventListener('click', () => {
 toast.style.animation = 'slideOut 0.3s forwards';
 setTimeout(() => {
 toast.remove();
 }, 300);
 });
 
 // Auto remove after 5 seconds
 setTimeout(() => {
 if (toast.parentNode) {
 toast.style.animation = 'slideOut 0.3s forwards';
 setTimeout(() => {
 if (toast.parentNode) toast.remove();
 }, 300);
 }
 }, 5000);
}

// Format Date
function formatDate(dateString) {
 const date = new Date(dateString);
 return date.toLocaleDateString('en-US', { 
 year: 'numeric', 
 month: 'short', 
 day: 'numeric' 
 });
}

// Format Duration
function formatDuration(seconds) {
 const minutes = Math.floor(seconds / 60);
 const remainingSeconds = seconds % 60;
 return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
}

// Initialize App
document.addEventListener('DOMContentLoaded', initApp);