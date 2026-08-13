import sys

with open('api.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace interceptor and enable withCredentials
new_setup = '''
const apiClient = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
  withCredentials: true, // Required for HttpOnly cookies
});
'''

# Remove interceptor completely
import re
content = re.sub(r'const apiClient = axios\.create\(\{.*?\}\);', new_setup.strip(), content, flags=re.DOTALL)
content = re.sub(r'apiClient\.interceptors\.request\.use.*?\}\);', '', content, flags=re.DOTALL)

# Add logout, verifyEmail, forgotPassword, resetPassword
auth_additions = '''
const logout = async () => {
  const res = await apiClient.post('/api/auth/logout');
  return res.data;
};

const verifyEmail = async (token) => {
  const res = await apiClient.post('/api/auth/verify-email', { token });
  return res.data;
};

const forgotPassword = async (email) => {
  const res = await apiClient.post('/api/auth/forgot-password', { email });
  return res.data;
};

const resetPassword = async (token, password) => {
  const res = await apiClient.post('/api/auth/reset-password', { token, password });
  return res.data;
};
'''

content = content.replace('const getMe = async () => {', auth_additions + '\\nconst getMe = async () => {')

content = content.replace('getMe,', 'getMe,\\n  logout,\\n  verifyEmail,\\n  forgotPassword,\\n  resetPassword,')

with open('api.js', 'w', encoding='utf-8') as f:
    f.write(content)

print('Updated api.js')
