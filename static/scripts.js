function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/static/login.html';
}

// Check token validity on page load
document.addEventListener('DOMContentLoaded', async () => {
    const token = localStorage.getItem('token');
    if (token && window.location.pathname !== '/static/chat.html') {
        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` },
                body: JSON.stringify({ message: 'ping' })
            });
            if (!response.ok && response.status === 401) {
                logout();
            }
        } catch (error) {
            logout();
        }
    }
});