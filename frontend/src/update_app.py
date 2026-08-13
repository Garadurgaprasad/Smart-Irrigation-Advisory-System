import sys

with open('App.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

imports = '''import VerifyEmail from './pages/VerifyEmail';
import ForgotPassword from './pages/ForgotPassword';
import ResetPassword from './pages/ResetPassword';
'''

content = content.replace('import AdminPanel from \\'./pages/AdminPanel\\';', 'import AdminPanel from \\'./pages/AdminPanel\\';\\n' + imports)

routes = '''
          <Route path="/verify-email" element={<VerifyEmail />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/reset-password" element={<ResetPassword />} />
'''

content = content.replace('<Route path="/register"', routes + '\\n          <Route path="/register"')

with open('App.jsx', 'w', encoding='utf-8') as f:
    f.write(content)

print('Updated App.jsx')
